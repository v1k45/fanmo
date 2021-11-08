export default function({ $axios }) {
  $axios.defaults.xsrfHeaderName = 'X-CSRFTOKEN';
  $axios.defaults.xsrfCookieName = 'csrftoken';
}
