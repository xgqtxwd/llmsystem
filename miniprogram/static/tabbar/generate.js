// Generate tabbar PNG icons as base64 data URIs
const fs = require('fs')
const path = require('path')

// Simple 1x1 transparent PNG + SVG fallback for uni-app H5
// uni-app TabBar requires actual image files
// For H5 mode we'll use emoji-based CSS approach instead

const tabbarDir = path.join(__dirname)
if (!fs.existsSync(tabbarDir)) {
  fs.mkdirSync(tabbarDir, { recursive: true })
}

// Create a minimal 1x1 PNG (smallest valid PNG)
const pixelPNG = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==', 'base64')

const icons = ['home.png', 'home-active.png', 'chat.png', 'chat-active.png', 'recipes.png', 'recipes-active.png', 'profile.png', 'profile-active.png']

for (const icon of icons) {
  const iconPath = path.join(tabbarDir, icon)
  if (!fs.existsSync(iconPath)) {
    fs.writeFileSync(iconPath, pixelPNG)
    console.log(`Created: ${icon}`)
  }
}

console.log('All tabbar icons created!')
