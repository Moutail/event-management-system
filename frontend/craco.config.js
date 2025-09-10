module.exports = {
  webpack: {
    configure: (webpackConfig) => {
      // Désactiver complètement les source maps en production
      if (process.env.NODE_ENV === 'production' || process.env.GENERATE_SOURCEMAP === 'false') {
        webpackConfig.devtool = false;
        
        // Supprimer tous les loaders de source maps
        webpackConfig.module.rules.forEach((rule) => {
          if (rule.use && rule.use.some(use => use.loader && use.loader.includes('source-map-loader'))) {
            rule.use = rule.use.filter(use => !use.loader || !use.loader.includes('source-map-loader'));
          }
        });
      }
      
      // Configuration pour Vercel - optimisations
      webpackConfig.resolve = webpackConfig.resolve || {};
      webpackConfig.resolve.fallback = {
        ...webpackConfig.resolve.fallback,
        "fs": false,
        "path": false,
        "os": false,
        "crypto": false,
        "stream": false,
        "util": false,
        "buffer": false
      };
      
      // Optimisations pour la production
      if (process.env.NODE_ENV === 'production') {
        webpackConfig.optimization = webpackConfig.optimization || {};
        webpackConfig.optimization.splitChunks = {
          chunks: 'all',
          cacheGroups: {
            vendor: {
              test: /[\\/]node_modules[\\/]/,
              name: 'vendors',
              chunks: 'all',
            },
          },
        };
      }
      
      return webpackConfig;
    },
  },
  // Configuration Babel optimisée
  babel: {
    presets: [
      ['@babel/preset-env', { 
        targets: { 
          browsers: ['>0.2%', 'not dead', 'not op_mini all'] 
        },
        modules: false
      }],
      ['@babel/preset-react', { runtime: 'automatic' }]
    ]
  }
};
