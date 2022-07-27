#!/usr/bin/env node

import { App } from 'aws-cdk-lib';
import FanmoStack from '../lib/fanmo-stack.js';

const app = new App();
new FanmoStack(app, 'fanmo-web', {
  env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: 'ap-south-1' },
});
