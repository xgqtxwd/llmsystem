import fs from 'fs'
import path from 'path'

// Generate simple PNG-like placeholder icons as base64 data URIs
// Since we can't create actual PNG files easily, we'll use SVG icons which uni-app H5 supports
const icons = {
  'home.svg': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024"><path d="M896 448L512 128 128 448v448h768V448z" fill="#999"/></svg>`,
  'home-active.svg': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024"><path d="M896 448L512 128 128 448v448h768V448z" fill="#10b981"/></svg>`,
  'chat.svg': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024"><path d="M896 640V384c0-35.35-28.65-64-64-64H192c-35.35 0-64 28.65-64 64v256c0 35.35 28.65 64 64 64h128l64 64 64-64h384c35.35 0 64-28.65 64-64z" fill="#999"/></svg>`,
  'chat-active.svg': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024"><path d="M896 640V384c0-35.35-28.65-64-64-64H192c-35.35 0-64 28.65-64 64v256c0 35.35 28.65 64 64 64h128l64 64 64-64h384c35.35 0 64-28.65 64-64z" fill="#10b981"/></svg>`,
  'recipes.svg': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024"><path d="M832 128H320v768h512V128zM192 256H128v640h64V256z" fill="#999"/></svg>`,
  'recipes-active.svg': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024"><path d="M832 128H320v768h512V128zM192 256H128v640h64V256z" fill="#10b981"/></svg>`,
  'profile.svg': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024"><path d="M512 512c106.04 0 192-85.96 192-192s-85.96-192-192-192-192 85.96-192 192 85.96 192 192 192zM128 896h768c0-212.13-169.87-384-384-384s-384 171.87-384 384z" fill="#999"/></svg>`,
  'profile-active.svg': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024"><path d="M512 512c106.04 0 192-85.96 192-192s-85.96-192-192-192-192 85.96-192 192 85.96 192 192 192zM128 896h768c0-212.13-169.87-384-384-384s-384 171.87-384 384z" fill="#10b981"/></svg>`
}

const dir = path.dirname(process.argv[1])
const staticDir = path.join(dir, 'static', 'tabbar')

if (!fs.existsSync(staticDir)) {
  fs.mkdirSync(staticDir, { recursive: true })
}

for (const [name, content] of Object.entries(icons)) {
  fs.writeFileSync(path.join(staticDir, name), content)
  console.log(`Created ${name}`)
}

console.log('All tabbar icons created!')
