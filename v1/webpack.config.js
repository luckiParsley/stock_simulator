const path = require('path');

module.exports = {
    entry: './static/js/main.js',
    output: {
        path: path.resolve(__dirname, 'static/dist'),
        filename: 'bundle.js'
    },
    module: {
        rules: [
            {
                test: /\.jsx?$/,
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: ['@babel/preset-react']
                    }
                }
            }
        ]
    },
    resolve: {
        extensions: ['.js', '.jsx']
    }
};