import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as rds from 'aws-cdk-lib/aws-rds';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';
import { readFileSync } from 'fs';


const config = {
  ec2: {
    machineImage: 'ami-0325e3016099f9112',
    keyPair: 'fanmo'
  },
  rds: {
    dbName: 'fanmo',
    username: 'postgres'
  }
}


class FanmoStack extends cdk.Stack {

  constructor(scope, id, props) {
    super(scope, id, props);

    this.setupNetworking()
    this.setupRole()
    this.setupStorage()
    this.setupWebserver()
    this.setupDbServer()

    new cdk.CfnOutput(this, 'ServerIP', { value: this.ec2Instance.instancePublicIp })
    new cdk.CfnOutput(this, 'BucketName', { value: this.s3Bucket.bucketName })
    new cdk.CfnOutput(this, 'CDNDist', { value: this.cfDistribution.distributionDomainName })
    new cdk.CfnOutput(this, 'CDNKeyGroupId', { value: this.cfKeyGroup.keyGroupId })
    new cdk.CfnOutput(this, 'DBHost', { value: this.dbInstance.instanceEndpoint.hostname });
    new cdk.CfnOutput(this, 'DBSecret', { value: this.dbInstance.secret.secretName });
  }

  /**
   * Create VPC and Security Group
   */
  setupNetworking() {
    this.vpc = new ec2.Vpc(this, 'VPC', {
      cidr: '10.0.0.0/16',
      natGateways: 0,
      subnetConfiguration: [
        { name: 'public', cidrMask: 24, subnetType: ec2.SubnetType.PUBLIC },
        { name: 'isolated', cidrMask: 24, subnetType: ec2.SubnetType.PRIVATE_ISOLATED },
      ],
    });

    this.securityGroup = new ec2.SecurityGroup(this, 'SecurityGroup', {
      vpc: this.vpc,
      allowAllOutbound: true,
    });

    this.securityGroup.addIngressRule(
      ec2.Peer.anyIpv4(),
      ec2.Port.tcp(22),
      'Allow SSH access from anywhere',
    );

    this.securityGroup.addIngressRule(
      ec2.Peer.anyIpv4(),
      ec2.Port.tcp(80),
      'Allow HTTP traffic from anywhere',
    );

    this.securityGroup.addIngressRule(
      ec2.Peer.anyIpv4(),
      ec2.Port.tcp(443),
      'Allow HTTPS traffic from anywhere',
    );

    this.ip = new ec2.CfnEIP(this, 'PublicIP')
  }

  setupRole() {
    this.iamRole = new iam.Role(this, 'ServiceRole', {
      assumedBy: new iam.ServicePrincipal('ec2.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonS3FullAccess'),
        iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonSSMReadOnlyAccess'),
        iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonSESFullAccess'),
        iam.ManagedPolicy.fromAwsManagedPolicyName('CloudWatchAgentServerPolicy'),
      ],
    });
  }

  setupStorage() {
    this.s3Bucket = new s3.Bucket(this, 'MediaStorage');

    // Grant access to cloudfront
    const cloudfrontOAI = new cloudfront.OriginAccessIdentity(this, 'CDNIdentity');
    this.s3Bucket.addToResourcePolicy(new iam.PolicyStatement({
      actions: ['s3:GetObject'],
      resources: [this.s3Bucket.arnForObjects('*')],
      principals: [new iam.CanonicalUserPrincipal(cloudfrontOAI.cloudFrontOriginAccessIdentityS3CanonicalUserId)]
    }));

    // key group for private content
    this.cfKeyGroup = new cloudfront.KeyGroup(this, 'KeyGroup', {
      items: [
        new cloudfront.PublicKey(this, 'PublicKey', { encodedKey: readFileSync('./conf/cdn.pub', 'utf-8') })
      ]
    })

    // CloudFront distribution
    this.cfDistribution = new cloudfront.Distribution(this, 'CDN', {
      defaultBehavior: {
        origin: new origins.S3Origin(this.s3Bucket, { originAccessIdentity: cloudfrontOAI }),
        compress: true,
        allowedMethods: cloudfront.AllowedMethods.ALLOW_GET_HEAD_OPTIONS,
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        trustedKeyGroups: [this.cfKeyGroup]
      }
    })

  }

  setupWebserver() {
    this.ec2Instance = new ec2.Instance(this, 'WebServer', {
      vpc: this.vpc,
      vpcSubnets: { subnetType: ec2.SubnetType.PUBLIC },
      role: this.iamRole,
      securityGroup: this.securityGroup,
      instanceType: ec2.InstanceType.of(
        ec2.InstanceClass.BURSTABLE2,
        ec2.InstanceSize.SMALL,
      ),
      machineImage: ec2.MachineImage.genericLinux({
        'ap-south-1': config.ec2.machineImage
      }),
      blockDevices: [
        {
          deviceName: '/dev/sda1',
          volume: ec2.BlockDeviceVolume.ebs(20)
        }
      ],
      keyName: config.ec2.keyPair,
    });
    this.ec2Instance.addUserData(readFileSync('./conf/user_data.sh', 'utf-8'))
    new ec2.CfnEIPAssociation(this, 'WebServerIP', { eip: this.ip.ref, instanceId: this.ec2Instance.instanceId })
  }

  setupDbServer() {
    this.dbInstance = new rds.DatabaseInstance(this, 'DBServer', {
      vpc: this.vpc,
      vpcSubnets: {
        subnetType: ec2.SubnetType.PRIVATE_ISOLATED,
      },
      engine: rds.DatabaseInstanceEngine.postgres({
        version: rds.PostgresEngineVersion.VER_14,
      }),
      instanceType: ec2.InstanceType.of(
        ec2.InstanceClass.BURSTABLE3,
        ec2.InstanceSize.MICRO,
      ),
      credentials: rds.Credentials.fromUsername(config.rds.username),
      multiAz: false,
      allocatedStorage: 10,
      maxAllocatedStorage: 15,
      allowMajorVersionUpgrade: false,
      autoMinorVersionUpgrade: true,
      backupRetention: cdk.Duration.days(1),
      deleteAutomatedBackups: true,
      deletionProtection: false,
      databaseName: config.rds.dbName,
      publiclyAccessible: false,
    });
    this.dbInstance.connections.allowFrom(this.ec2Instance, ec2.Port.tcp(5432));

  }

}

export default FanmoStack
