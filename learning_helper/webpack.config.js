const path = require('path');

module.exports = {
    context: path.resolve(__dirname),
    entry: './static/index.jsx',
    output: {
        path: path.resolve(__dirname, 'static'),
        filename: 'main.js'
    },
    module: {
        rules: [
            {
                test: /\.(js|jsx)$/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: ['@babel/preset-react', '@babel/preset-env'],
                        plugins: ['@babel/plugin-transform-runtime']
                    }
                },
                exclude: /node_modules/
            }
        ]
    },
    mode: 'development',
    resolve: {
        extensions: ['.js', '.jsx'],
        alias: {
            '@': path.resolve(__dirname, 'static'),
        },
    },
};