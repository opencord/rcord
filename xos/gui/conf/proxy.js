const httpProxy = require('http-proxy');

const target = process.env.PROXY || '192.168.46.100';

const apiProxy = httpProxy.createProxyServer({
  target: `http://${target}:9101`
});

const staticFilesProxy = httpProxy.createProxyServer({
  target: `http://${target}/spa`
});

apiProxy.on('error', (error, req, res) => {
  res.writeHead(500, {
    'Content-Type': 'text/plain'
  });
  console.error('[Proxy]', error);
});

staticFilesProxy.on('error', (error, req, res) => {
  res.writeHead(500, {
    'Content-Type': 'text/plain'
  });
  console.error('[Proxy]', error);
});

module.exports = {
  api: apiProxy,
  static: staticFilesProxy
};
