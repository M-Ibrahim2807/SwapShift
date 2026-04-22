# Real-Time Notifications - Quick Start Guide

## ✅ What's Already Done

Your app now has **real-time swap request notifications** that work without refreshing or re-logging in!

### Installation Complete ✓
- ✅ Notification polling system (every 2 seconds)
- ✅ Audio alert (800Hz beep)
- ✅ Toast messages
- ✅ Desktop notifications
- ✅ Global notification context
- ✅ Badge component for unread count
- ✅ Clean, refactored code

## 🚀 How It Works (For Users)

### Person A's Experience:
1. **Login** → App starts polling automatically
2. **Person B sends a swap request** → Instantly alerted:
   - 🔔 **Beep sound plays** (attention-grabbing)
   - 📬 **Toast message** pops up at bottom
   - 🔔 **Browser notification** appears (even if minimized)
3. **No refresh needed** → Everything happens automatically

### What Person A Does NOT Need To Do:
- ❌ Refresh page
- ❌ Re-login
- ❌ Close and reopen app
- ❌ Click anything to enable notifications
- ❌ Watch the screen constantly

## 📦 Files You Now Have

```
Frontend/src/
├── hooks/
│   └── useNotifications.js ..................... Real-time polling
├── context/
│   ├── AuthContext.jsx ......................... (already had)
│   ├── ToastContext.jsx ........................ (already had)
│   └── NotificationContext.jsx ................. NEW: Global notification state
├── components/
│   ├── LoadingSpinner/ ......................... (already had)
│   ├── Toast/ ................................. (already had)
│   └── NotificationBadge/ ...................... NEW: Unread count badge
│       ├── NotificationBadge.jsx
│       └── NotificationBadge.css
├── pages/
│   ├── EmployeeDashboard/
│   │   └── EmployeeDashboard.jsx .............. UPDATED: Cleaner code
│   └── ... (others unchanged)
├── App.jsx ................................... UPDATED: Added NotificationProvider
└── services/
    └── api.js ................................ (unchanged - uses existing endpoint)
```

## 🧪 Testing Steps (Must Do!)

### Test 1: Basic Notification
```
Device A: Login as Employee1
Device B: Login as Employee2
Device B: Request a shift swap to Employee1
Device A: Check for:
  ✓ Audio beep plays
  ✓ Toast message "You have 1 new swap request!"
  ✓ All without refreshing!
```

### Test 2: Desktop Notification
```
Device A: Login, grant notification permission when asked
Device B: Request a shift swap to Employee1
Device A: Minimize browser
Device B: Send another request (total 2)
Device A: Check for:
  ✓ Desktop notification appears (even while minimized)
  ✓ Shows "You have 1 new swap request!"
```

### Test 3: Multiple Notifications
```
Device A: Login
Device B & C: Each send a swap request to Employee1
Device A: Should see:
  ✓ Multiple beeps
  ✓ Toast: "You have 2 new swap requests!"
  ✓ Desktop notification
```

## 🎯 Key Features

| Feature | How It Works | When It Shows |
|---------|---|---|
| **Beep Sound** | 800Hz oscillator, 500ms duration | Always (unless muted) |
| **Toast Message** | Auto-dismisses in 3 seconds | Always |
| **Desktop Notification** | Requires user permission | Only if granted |
| **Polling** | Every 2 seconds while logged in | Continuously |
| **Badge Count** | Shows unread request count | On app navigation |

## ⚙️ Configuration

### To Change How Often It Checks (Polling Interval)
**File**: `src/pages/EmployeeDashboard/EmployeeDashboard.jsx` (line ~45)

```javascript
// Current: Every 2 seconds
useNotifications(token && role === 'employee', 2000);

// For every 5 seconds (less real-time, saves data):
useNotifications(token && role === 'employee', 5000);

// For every 1 second (very real-time, uses more data):
useNotifications(token && role === 'employee', 1000);
```

### To Change Alert Sound Pitch
**File**: `src/hooks/useNotifications.js` (line ~77)

```javascript
oscillator.frequency.value = 800; // Default beep

// Lower pitch (deeper):
oscillator.frequency.value = 600;

// Higher pitch (sharper):
oscillator.frequency.value = 1200;
```

### To Disable Notifications
```javascript
// In EmployeeDashboard.jsx, change to:
useNotifications(false, 2000); // Disabled
```

## 🔍 How to Verify It's Working

1. **Open Browser DevTools** (F12 → Console)
2. **Look for these messages**:
   ```
   ✓ "Notification permission granted"
   ✓ No console errors
   ✓ Each polling request to /api/v1/swap/inbox
   ```

3. **Check Network Tab**:
   - Should see GET requests to `/api/v1/swap/inbox`
   - Every 2 seconds (or your configured interval)
   - Status 200 OK

## 📊 What's Happening Behind the Scenes

```
App Initialization
    ↓
NotificationProvider wraps entire app
    ↓
User logs in
    ↓
EmployeeDashboard mounts
    ↓
useNotifications hook starts
    ↓
Every 2 seconds:
  - Poll /api/v1/swap/inbox
  - Compare count with previous
  - If NEW requests: alert!
    ↓
Cleanup when component unmounts
```

## 🎨 Optional: Add Badge to Navbar

To show the unread count badge in the navigation bar:

**File**: `src/components/Navbar/Navbar.jsx`

```jsx
import NotificationBadge from '../NotificationBadge/NotificationBadge';

export default function Navbar({ userName, role, onLogout }) {
  return (
    <nav className="navbar">
      <div className="navbar-content">
        <div className="navbar-logo">SwapShift</div>
        
        {/* Add this before the navbar-right div */}
        {role === 'employee' && <NotificationBadge />}
        
        <div className="navbar-right">
          {/* existing code */}
        </div>
      </div>
    </nav>
  );
}
```

## ✅ Verification Checklist

- [ ] No console errors on page load
- [ ] Audio beep works (test by requesting swap)
- [ ] Toast message appears (don't refresh!)
- [ ] Desktop notification permission was asked
- [ ] Desktop notification appears (minimize window to test)
- [ ] Polling continues without page refresh
- [ ] Multiple requests show correct count
- [ ] Works on multiple browser tabs
- [ ] Works while user browses other pages

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| No beep sound | Check browser/system volume, try different frequency |
| No toast message | Check console for errors, verify API endpoint |
| No desktop notification | Grant permission when prompted, check system settings |
| Badge not updating | Logout and login again, check if employee role |
| Polling stopped | Refresh page, check if token expired |

## 📝 What You Can Tell Users

> "You'll get instant notifications when someone requests a shift swap from you. You'll hear a beep, see a message, and even get a desktop alert - all without needing to refresh!"

## 🚀 Next Steps (Optional)

1. **Test thoroughly** - Use the testing steps above
2. **Deploy** - Push to production
3. **Monitor** - Check if notifications are working for all users
4. **Future improvements**:
   - WebSocket for zero-latency updates
   - Sound selection options
   - Notification history
   - Notification preferences

## 📞 Support

If notifications aren't working:
1. Check browser console for errors
2. Verify API endpoint is responding
3. Ensure user is logged in as employee
4. Check notification permission in browser settings
5. Try a different browser

---

**That's it!** Your app now has real-time notifications! 🎉
