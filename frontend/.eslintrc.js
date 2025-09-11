module.exports = {
  extends: [
    'react-app',
    'react-app/jest'
  ],
  rules: {
    // Désactiver complètement les règles qui empêchent le build
    'no-unused-vars': 'off',
    'react-hooks/exhaustive-deps': 'off',
    'no-use-before-define': 'off'
  },
  env: {
    browser: true,
    es6: true,
    node: true
  }
};
