# Skill: Biometric Authentication (React Native / Expo)

## Purpose
To securely authenticate users on mobile devices using built-in biometric hardware (Face ID, Touch ID, or Android Biometrics) via `expo-local-authentication`.

## When to Use
- When users need to log in frequently and want to avoid typing passwords
- When securing sensitive sections of an app (e.g., banking, personal data, settings)
- When implementing a "remember me" feature securely

## Procedure

### 1. Installation
Install the necessary Expo package:
```bash
npx expo install expo-local-authentication
```

### 2. Configuration (app.json)
Ensure your app requests the necessary permissions for iOS and Android.

```json
{
  "expo": {
    "ios": {
      "infoPlist": {
        "NSFaceIDUsageDescription": "This app uses Face ID to securely authenticate you and protect your data."
      }
    },
    "android": {
      "permissions": ["USE_BIOMETRIC", "USE_FINGERPRINT"]
    }
  }
}
```

### 3. Implementation Example
Create a custom hook or utility function to handle the authentication flow gracefully.

```tsx
import * as LocalAuthentication from 'expo-local-authentication';
import { useState, useEffect } from 'react';

export const useBiometricAuth = () => {
  const [isBiometricSupported, setIsBiometricSupported] = useState(false);

  useEffect(() => {
    (async () => {
      // 1. Check if hardware supports biometrics
      const compatible = await LocalAuthentication.hasHardwareAsync();
      
      // 2. Check if biometric records are enrolled on the device
      const enrolled = await LocalAuthentication.isEnrolledAsync();
      
      setIsBiometricSupported(compatible && enrolled);
    })();
  }, []);

  const authenticate = async (): Promise<boolean> => {
    if (!isBiometricSupported) {
      console.warn('Biometric authentication is not supported or enrolled.');
      return false;
    }

    try {
      const result = await LocalAuthentication.authenticateAsync({
        promptMessage: 'Authenticate to access your account',
        cancelLabel: 'Cancel', // Android only
        fallbackLabel: 'Use Passcode', // iOS only
        disableDeviceFallback: false, // Allow PIN fallback if biometrics fail
      });

      return result.success;
    } catch (error) {
      console.error('Biometric Auth Error:', error);
      return false;
    }
  };

  return { isBiometricSupported, authenticate };
};
```

### 4. Usage in Component
```tsx
import React from 'react';
import { View, Button, Text, Alert } from 'react-native';
import { useBiometricAuth } from './useBiometricAuth';

export const LoginScreen = () => {
  const { isBiometricSupported, authenticate } = useBiometricAuth();

  const handleLogin = async () => {
    const success = await authenticate();
    if (success) {
      Alert.alert('Success', 'You are securely logged in!');
      // Navigate to Dashboard
    } else {
      Alert.alert('Failed', 'Authentication failed or was canceled.');
    }
  };

  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      <Text>Welcome Back!</Text>
      {isBiometricSupported ? (
        <Button title="Login with Face ID / Touch ID" onPress={handleLogin} />
      ) : (
        <Button title="Login with Password" onPress={() => { /* fallback */ }} />
      )}
    </View>
  );
};
```

## Best Practices
- **Always provide a fallback**: Never force biometrics as the *only* login method. Devices break, sensors fail, and some users disable them. Always offer a password/PIN fallback.
- **Explain why**: Use `promptMessage` and `NSFaceIDUsageDescription` to clearly explain *why* the app needs biometrics.
- **Do not store passwords in plain text**: If using biometrics to unlock credentials, store the actual tokens securely using `expo-secure-store`.