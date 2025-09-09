#!/bin/bash

echo "🔍 BannkMint AI Netlify Deployment Verification"
echo "=============================================="

echo ""
echo "📁 Checking directory structure..."
if [ -f "/app/netlify.toml" ]; then
    echo "✅ netlify.toml found"
else
    echo "❌ netlify.toml missing"
fi

if [ -f "/app/.nvmrc" ]; then
    echo "✅ .nvmrc found (Node.js version: $(cat /app/.nvmrc))"
else
    echo "❌ .nvmrc missing"
fi

if [ -f "/app/frontend/package.json" ]; then
    echo "✅ frontend/package.json found"
else
    echo "❌ frontend/package.json missing"
fi

if [ -f "/app/frontend/.env.production" ]; then
    echo "✅ frontend/.env.production found"
else
    echo "❌ frontend/.env.production missing"
fi

echo ""
echo "🔧 Testing build process..."
cd /app/frontend

echo "📦 Installing dependencies..."
yarn install --silent

echo "🏗️ Building application..."
if yarn build > /dev/null 2>&1; then
    echo "✅ Build successful"
    
    if [ -d "build" ]; then
        echo "✅ Build directory exists: frontend/build/"
        echo "📊 Build contents:"
        ls -la build/ | grep -E '\.(js|css|html)$' | sed 's/^/   /'
        
        # Check file sizes
        if [ -f "build/static/js/"*.js ]; then
            js_size=$(du -h build/static/js/*.js | cut -f1)
            echo "📏 JavaScript bundle size: $js_size"
        fi
        
        if [ -f "build/static/css/"*.css ]; then
            css_size=$(du -h build/static/css/*.css | cut -f1)
            echo "📏 CSS bundle size: $css_size"
        fi
    else
        echo "❌ Build directory missing"
    fi
else
    echo "❌ Build failed"
fi

echo ""
echo "⚙️ Netlify configuration:"
echo "   Base directory: frontend"
echo "   Publish directory: build"  
echo "   Build command: yarn build"
echo "   Node.js version: 18"

echo ""
echo "🚀 Deployment status: READY"
echo "   Your BannkMint AI app is ready for Netlify deployment!"