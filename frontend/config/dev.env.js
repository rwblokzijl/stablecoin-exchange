var merge = require('webpack-merge')
var prodEnv = require('./prod.env')

module.exports = merge(prodEnv, {
  NODE_ENV: '"development"',
  // devServer: {
  //   proxy: "http://localhost:8000"
  // }
  proxyTable: {
    "/api": {
      target: "http://localhost:8000",
      pathRewrite: { "/api": "" },
      changeOrigin: true,
      logLevel: "debug"
    }
  }
})
