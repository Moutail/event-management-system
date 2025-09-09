module.exports = {
  webpack: {
    configure: (webpackConfig) => {
      // Désactiver les avertissements de source maps
      webpackConfig.module.rules.forEach((rule) => {
        if (rule.use && rule.use.some(use => use.loader && use.loader.includes('source-map-loader'))) {
          rule.use = rule.use.filter(use => !use.loader || !use.loader.includes('source-map-loader'));
        }
      });
      
      // Configuration pour Vercel
      webpackConfig.resolve = webpackConfig.resolve || {};
      webpackConfig.resolve.fallback = {
        ...webpackConfig.resolve.fallback,
        "fs": false,
        "path": false,
        "os": false
      };
      
      return webpackConfig;
    },
  },
  // Configuration pour Vercel
  babel: {
    presets: [
      ['@babel/preset-env', { targets: { node: 'current' } }],
      ['@babel/preset-react', { runtime: 'automatic' }]
    ]
  }
};
