# Navigation Redesign - Testing Steps

## Quick Test Commands

### 1. Verify Services Running
```bash
cd /home/ubuntu/enms
docker compose ps | grep -E "(nginx|auth-service)"
```

### 2. Test Public Pages (Guest User)
```bash
# Open in browser:
http://YOUR_SERVER_IP:8080/about.html
http://YOUR_SERVER_IP:8080/iso50001.html
http://YOUR_SERVER_IP:8080/contact.html

# Expected:
- Hamburger menu visible
- Click hamburger → sidebar opens
- See: About, ISO 50001, Contact, Sign In
- Do NOT see: Dashboard links, Admin Dashboard, Logout
```

### 3. Test Login
```bash
# Open: http://YOUR_SERVER_IP:8080/auth.html
# Login with: test@gmail.com / Test123

# After login, should redirect to: http://YOUR_SERVER_IP:8080/
```

### 4. Test Dashboard (Authenticated User)
```bash
# On index.html after login:
# Expected in sidebar:
- About, ISO 50001, Contact (public pages)
- Dashboard, Analytics, Reports, Grafana, Node-RED, Simulator
- Logout
# Do NOT see: Sign In, Admin Dashboard
```

### 5. Test Admin Access
```bash
# Logout and login with admin:
# Email: swe.mohamad.jarad@gmail.com OR umut.ogur@aartimuhendislik.com
# Password: (your password)

# Expected in sidebar:
- All regular user items PLUS
- Admin Dashboard (with orange tint)
```

## Manual Verification Checklist

### Visual Design
- [ ] Sidebar slides in from left smoothly (300ms animation)
- [ ] Dark overlay appears behind sidebar
- [ ] Blue gradient background (#1e3a8a → #0a2463)
- [ ] Links have left border on hover (#00A8E8)
- [ ] Admin Dashboard has orange tint
- [ ] Logout button is red-tinted

### Functionality
- [ ] Hamburger button toggles sidebar open/close
- [ ] Close (×) button closes sidebar
- [ ] Clicking overlay closes sidebar
- [ ] All links navigate correctly
- [ ] User name displays in top right (when authenticated)

### Conditional Display
- [ ] Guest: See public pages + Sign In only
- [ ] Authenticated: See public + dashboard pages + Logout
- [ ] Admin: See all above + Admin Dashboard

### Cross-Page Consistency
- [ ] Sidebar identical on all pages
- [ ] Navigation works from any page
- [ ] Logos display correctly (APlus, HUMANERGY, WASABI)

## Expected Behavior Summary

| Page | Guest | User | Admin |
|------|-------|------|-------|
| about.html | ✅ Sidebar with Sign In | ✅ Sidebar with Dashboard | ✅ Full sidebar |
| iso50001.html | ✅ Sidebar with Sign In | ✅ Sidebar with Dashboard | ✅ Full sidebar |
| contact.html | ✅ Sidebar with Sign In | ✅ Sidebar with Dashboard | ✅ Full sidebar |
| index.html | ❌ Redirects to auth | ✅ Sidebar with Dashboard | ✅ Full sidebar + Admin |

## Troubleshooting

### Sidebar doesn't open
Check browser console (F12) for errors. Common issues:
- CSS file not loaded: Check `/css/sidebar.css` accessible
- JS file not loaded: Check `/js/sidebar.js` accessible
- Function not defined: Ensure script loaded before calling

### Wrong links visible
Check localStorage in browser console:
```javascript
localStorage.getItem('auth_token')
localStorage.getItem('user_data')
```

### Styling broken
- Clear browser cache (Ctrl+Shift+R)
- Check for CSS conflicts in browser inspector
- Verify sidebar.css loaded (Network tab)

## Success Criteria
✅ All pages have working hamburger menu  
✅ Sidebar adapts based on authentication  
✅ Admin users see Admin Dashboard  
✅ All navigation links work correctly  
✅ Design consistent across pages  
✅ No JavaScript errors in console  
