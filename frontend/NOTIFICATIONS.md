# Real-Time Swap Request Notifications

## Overview
Person A now receives **instant notifications** when Person B requests a swap - **without needing to refresh or login again**.

## How It Works

### 1. **Real-Time Polling System**
- The app polls the swap inbox **every 2 seconds** while the user is logged in
- Custom hook `useNotifications` automatically detects new swap requests
- No manual refresh needed!

### 2. **Three-Layer Notification System**

#### Layer 1: **Audio Alert** 🔔
- 800Hz beep tone plays instantly (500ms duration)
- Attention-grabbing without being annoying
- Uses Web Audio API (works in all modern browsers)

#### Layer 2: **Toast Notification** 
- Message pops up at the bottom of the screen
- Displays: "You have 1 new swap request!"
- Auto-dismisses after 3 seconds
- Works even while user is on any page

#### Layer 3: **Browser Notification**
- Desktop/mobile system notification
- Requires one-time permission
- Shows: "🔔 SwapShift Alert"
- **Requires interaction** - stays visible until user clicks it
- Shows even if app window is minimized

### 3. **Components & Files**

```
Frontend Real-Time System:
├── hooks/
│   └── useNotifications.js          # Polling logic & sound
├── context/
│   └── NotificationContext.jsx      # Global notification state
├── components/
│   └── NotificationBadge/           # Visual badge with count
│       ├── NotificationBadge.jsx
│       └── NotificationBadge.css
├── pages/
│   └── EmployeeDashboard.jsx        # Uses useNotifications hook
└── App.jsx                          # Wraps with NotificationProvider
```

## Usage

### For Employees (Person A):

1. **Login to the app** - Notifications start automatically
2. **Requested browser permission?** - Click "Allow" for desktop alerts
3. **When Person B sends a swap request:**
   - ✅ Audio beep plays
   - ✅ Toast message appears
   - ✅ Browser notification shows (even if app is minimized)
   - ✅ Badge updates with unread count

### No Actions Needed:
- ❌ No refresh required
- ❌ No re-login needed
- ❌ Can work on other tabs/windows
- ❌ Works even with app minimized (if desktop notifications enabled)

## Configuration

### Adjust Polling Interval
In `EmployeeDashboard.jsx`:
```javascript
// Poll every 2000ms (2 seconds)
useNotifications(token && role === 'employee', 2000);

// To change to 5 seconds:
useNotifications(token && role === 'employee', 5000);
```

### Adjust Notification Sound
In `hooks/useNotifications.js`:
```javascript
oscillator.frequency.value = 800;  // 800Hz beep
// Change to 600 for lower pitch, 1000 for higher pitch
```

## API Endpoints Used

The system uses the existing API:
```
GET /api/v1/swap/inbox
```

This endpoint returns an array of pending swap requests. The hook compares the count with the previous count to detect new requests.

## Browser Support

| Feature | Chrome | Firefox | Safari | Edge |
|---------|--------|---------|--------|------|
| Audio Beep | ✅ | ✅ | ✅ | ✅ |
| Toast Popup | ✅ | ✅ | ✅ | ✅ |
| Desktop Notifications | ✅ | ✅ | ✅ | ✅ |

## Testing the Notifications

### Test Scenario:
1. **Person A**: Login and stay on dashboard
2. **Person B**: Send a swap request to Person A
3. **Expected Result**:
   - 🔔 Beep plays
   - 📬 Toast message shows
   - 🔔 Browser notification appears
   - All without Person A refreshing or logging in again!

## Security Notes

- ✅ Token is securely stored and automatically sent with requests
- ✅ Expired tokens are caught by the API interceptor
- ✅ No sensitive data stored in localStorage beyond token
- ✅ Notifications are read-only (don't modify anything)

## Performance Considerations

- **Polling every 2 seconds**: Minimal overhead (~5KB per request)
- **Audio Context**: Single instance per notification (destroyed after sound)
- **Browser Notifications**: Only if user granted permission
- **Background**: Continues polling even if app tab is not in focus

## Future Enhancements

Possible improvements:
1. **WebSocket instead of polling** - Real-time updates (zero latency)
2. **Service Workers** - Notifications even when app is closed
3. **Push Notifications** - Mobile app integration
4. **Sound Options** - Choose different alert sounds
5. **Notification Preferences** - Toggle beep, toast, or desktop alerts
