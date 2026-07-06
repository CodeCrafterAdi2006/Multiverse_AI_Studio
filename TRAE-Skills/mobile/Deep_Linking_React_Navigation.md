# Skill: Deep Linking in React Navigation

## Purpose
To allow users to open specific screens within a React Native app directly from external sources (e.g., a web browser, email, push notification, or SMS) using a custom URL scheme or universal links.

## When to Use
- When sending password reset links or email verification links that should open the app
- When sharing content (e.g., a specific product or profile) via social media
- When redirecting users back to the app after an OAuth login flow in the browser

## Procedure

### 1. Configuration (app.json)
Define a custom scheme for your app. If your app is named "MyApp", the scheme could be `myapp`.

```json
{
  "expo": {
    "scheme": "myapp",
    "android": {
      "intentFilters": [
        {
          "action": "VIEW",
          "data": [
            { "scheme": "myapp" },
            { "scheme": "https", "host": "myapp.com", "pathPrefix": "/" }
          ],
          "category": ["BROWSABLE", "DEFAULT"]
        }
      ]
    },
    "ios": {
      "associatedDomains": ["applinks:myapp.com"]
    }
  }
}
```

### 2. Configure React Navigation
Create a linking configuration object to map URL paths to your navigation screens.

```typescript
import * as Linking from 'expo-linking';
import { NavigationContainer, LinkingOptions } from '@react-navigation/native';

// Define the linking configuration
const linking: LinkingOptions<RootStackParamList> = {
  // Use expo-linking to automatically get the scheme
  prefixes: [Linking.createURL('/'), 'https://myapp.com'],
  config: {
    screens: {
      Home: 'home',
      Profile: 'user/:id', // maps to myapp://user/123
      Settings: 'settings',
      NotFound: '*', // Catch-all for invalid links
    },
  },
};

export default function App() {
  return (
    <NavigationContainer linking={linking} fallback={<Text>Loading...</Text>}>
      <RootNavigator />
    </NavigationContainer>
  );
}
```

### 3. Handling Parameters in Screens
When a deep link like `myapp://user/123` is opened, React Navigation automatically passes the `id` as a route parameter to the `Profile` screen.

```tsx
import React from 'react';
import { View, Text } from 'react-native';
import { NativeStackScreenProps } from '@react-navigation/native-stack';

type Props = NativeStackScreenProps<RootStackParamList, 'Profile'>;

export const ProfileScreen = ({ route }: Props) => {
  // 'id' is extracted from the deep link URL automatically
  const { id } = route.params;

  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      <Text>User Profile ID: {id}</Text>
    </View>
  );
};
```

### 4. Testing Deep Links
You can test deep links locally using the Expo CLI.

**For iOS Simulator:**
```bash
npx uri-scheme open myapp://user/456 --ios
```

**For Android Emulator:**
```bash
npx uri-scheme open myapp://user/456 --android
```

## Best Practices
- **Universal Links (iOS) and App Links (Android)**: While custom schemes (`myapp://`) are easy, they can clash. For production, configure Universal Links/App Links (`https://myapp.com`) which require hosting an `apple-app-site-association` and `assetlinks.json` file on your web server.
- **Graceful Fallbacks**: Always provide a `NotFound` screen in your linking config to handle malformed or outdated URLs gracefully.
- **Authentication State**: If a deep link points to a protected screen, ensure your navigation logic checks the auth state and redirects to the Login screen, ideally preserving the original deep link intent to redirect back after login.