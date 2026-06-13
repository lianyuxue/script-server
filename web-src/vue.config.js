const webpack = require('webpack');

module.exports = {
    // don't set absolute paths, otherwise reverse proxies with a custom path won't work
    publicPath: '',

    outputDir: '../web',

    devServer: {
        port: 8080,
        https: false,
        hot: true,
        liveReload: true,
        proxy: {
            '/api': {
                target: 'http://127.0.0.1:5001',
                changeOrigin: true,
                logLevel: 'debug'
            },
            '/scripts': {
                target: 'http://127.0.0.1:5001',
                changeOrigin: true,
                ws: true,
                logLevel: 'debug',
                onProxyRes: function (proxyRes, req, res) {
                    proxyRes.on('error', function (err) {
                        console.error('Proxy Res Error:', err);
                    });
                },
                onError: function (err, req, res) {
                    console.error('Proxy Error:', err);
                }
            },
            '/logs': {
                target: 'http://127.0.0.1:5001',
                changeOrigin: true,
                logLevel: 'debug'
            },
            '/auth': {
                target: 'http://127.0.0.1:5001',
                changeOrigin: true,
                logLevel: 'debug'
            },
            '/theme': {
                target: 'http://127.0.0.1:5001',
                changeOrigin: true,
                logLevel: 'debug'
            },
            '/conf': {
                target: 'http://127.0.0.1:5001',
                changeOrigin: true,
                logLevel: 'debug'
            },
            '/executions': {
                target: 'http://127.0.0.1:5001',
                ws: true,
                changeOrigin: true,
                logLevel: 'debug',
                onError: function (err, req, res) {
                    console.error('Proxy Error (executions):', err);
                }
            },
            '/history': {
                target: 'http://127.0.0.1:5001',
                changeOrigin: true,
                logLevel: 'debug'
            }
        }
    },

    pages: {
        index: {
            entry: 'src/main-app/index.js',
            template: 'public/index.html',
            chunks: ['chunk-index-vendors', 'index']
        },
        admin: {
            entry: 'src/admin/admin.js',
            template: 'public/admin.html',
            chunks: ['chunk-admin-vendors', 'admin']
        },
        login: {
            entry: 'src/login/login.js',
            template: 'public/login.html',
            chunks: ['chunk-login-vendors', 'login']
        }
    },

    css: {
        loaderOptions: {
            scss: {
                additionalData: '@import "./src/assets/css/color_variables.scss"; '
                    + '@import "materialize-css/sass/components/_variables.scss"; '
                    + '@import "materialize-css/sass/components/_global.scss"; '
                    + '@import "materialize-css/sass/components/_typography.scss"; '
            }
        }
    },

    configureWebpack: {},

    chainWebpack: config => {
        const options = module.exports;
        const pages = options.pages;
        const pageKeys = Object.keys(pages);

        const IS_VENDOR = /[\\/]node_modules[\\/]/;

        // ATTENTION! do not use minSize/maxSize until vue-cli moved to the 4th version of html-webpack-plugin
        // Otherwise plugin won't be able to find split packages
        config.optimization
            .splitChunks({
                cacheGroups: {
                    ...pageKeys.map(key => ({
                        name: `chunk-${key}-vendors`,
                        priority: -11,
                        chunks: chunk => chunk.name === key,
                        test: IS_VENDOR,
                        enforce: true
                    }))
                }
            });
    },

    pluginOptions: {
        karma: {
            files: ['tests/unit/index.js'],
            customLaunchers: {
                ChromeHeadless: {
                    base: 'Chrome',
                    flags: [
                        '--headless',
                        '--disable-gpu',
                        '--no-sandbox',
                        '--remote-debugging-port=9222'
                    ]
                }
            },
            browsers: ['Chrome', 'Firefox'],

            reporters: ['mocha', 'allure'],

            frameworks: ['mocha'],

            allureReport: {
                reportDir: '/tmp/allure_result',
                useBrowserName: true
            },

            plugins: [
                'karma-chrome-launcher',
                'karma-firefox-launcher',
                'karma-sourcemap-loader',
                'karma-webpack',
                'karma-mocha',
                'karma-mocha-reporter',
                'karma-allure-reporter'
            ]
        }
    }
};