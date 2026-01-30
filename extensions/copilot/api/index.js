/**
 * Vercel Serverless Function Entry Point
 * This file is used by Vercel to handle all requests
 */

const app = require('../dist/index.js').default;
module.exports = app;
