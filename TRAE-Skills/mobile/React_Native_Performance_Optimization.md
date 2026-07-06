# Skill: React Native Performance Optimization

## Purpose
To optimize React Native applications for better performance, smooth animations, and reduced memory usage.

## When to Use
- When your app feels slow or janky
- For optimizing list performance
- When reducing bundle size
- For improving startup time
- When optimizing animation smoothness

## Procedure

### 1. List Optimization with FlatList
Optimize long lists with proper configuration.

```tsx
import React from 'react';
import { FlatList, Text, View, StyleSheet } from 'react-native';

const data = Array.from({ length: 1000 }, (_, i) => ({ id: i.toString(), text: `Item ${i}` }));

const Item = React.memo(({ item }) => (
  <View style={styles.item}>
    <Text style={styles.text}>{item.text}</Text>
  </View>
));

export default function OptimizedFlatList() {
  const renderItem = React.useCallback(({ item }) => (
    <Item item={item} />
  ), []);

  const keyExtractor = React.useCallback((item) => item.id, []);

  return (
    <FlatList
      data={data}
      renderItem={renderItem}
      keyExtractor={keyExtractor}
      initialNumToRender={10}
      maxToRenderPerBatch={10}
      windowSize={5}
      removeClippedSubviews={true}
      getItemLayout={(data, index) => ({
        length: 50,
        offset: 50 * index,
        index,
      })}
    />
  );
}

const styles = StyleSheet.create({
  item: {
    height: 50,
    padding: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  text: {
    fontSize: 16,
  },
});
```

### 2. Image Optimization
Optimize images for faster loading and less memory.

```tsx
import React from 'react';
import { Image, StyleSheet, Dimensions } from 'react-native';
import FastImage from 'react-native-fast-image';

const { width: screenWidth } = Dimensions.get('window');

export default function OptimizedImage() {
  return (
    <>
      {/* Use FastImage for better performance */}
      <FastImage
        style={styles.image}
        source={{
          uri: 'https://example.com/image.jpg',
          priority: FastImage.priority.normal,
          cache: FastImage.cacheControl.immutable,
        }}
        resizeMode={FastImage.resizeMode.cover}
      />
      
      {/* Or use optimized local images */}
      <Image
        style={styles.image}
        source={require('./assets/optimized-image.png')}
        resizeMethod="resize"
        resizeMode="cover"
      />
    </>
  );
}

const styles = StyleSheet.create({
  image: {
    width: screenWidth,
    height: 200,
  },
});
```

### 3. State Management Optimization
Avoid unnecessary re-renders.

```tsx
import React, { useState, useMemo, useCallback } from 'react';
import { View, Text, Button, StyleSheet } from 'react-native';

// Memoize components that don't need to re-render
const ExpensiveComponent = React.memo(({ data }) => {
  console.log('ExpensiveComponent re-rendered');
  return <Text>{data}</Text>;
});

export default function StateOptimization() {
  const [count, setCount] = useState(0);
  const [text, setText] = useState('');

  // Memoize expensive calculations
  const expensiveData = useMemo(() => {
    console.log('Calculating expensive data...');
    return `Count: ${count * 2}`;
  }, [count]); // Only recalculate when count changes

  // Memoize callbacks
  const handleIncrement = useCallback(() => {
    setCount(c => c + 1);
  }, []);

  return (
    <View style={styles.container}>
      <ExpensiveComponent data={expensiveData} />
      <Button title="Increment" onPress={handleIncrement} />
      <TextInput
        value={text}
        onChangeText={setText}
        placeholder="Type something..."
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
  },
});
```

### 4. Animation Optimization with Reanimated
Use Reanimated for smooth animations.

```tsx
import React from 'react';
import { View, StyleSheet, TouchableOpacity } from 'react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  withTiming,
  Easing,
} from 'react-native-reanimated';

export default function ReanimatedAnimation() {
  const scale = useSharedValue(1);
  const opacity = useSharedValue(1);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
    opacity: opacity.value,
  }));

  const onPress = () => {
    scale.value = withSpring(0.95, { damping: 10, stiffness: 100 });
    opacity.value = withTiming(0.5, { duration: 200, easing: Easing.ease });
    
    setTimeout(() => {
      scale.value = withSpring(1);
      opacity.value = withTiming(1);
    }, 200);
  };

  return (
    <View style={styles.container}>
      <TouchableOpacity onPress={onPress}>
        <Animated.View style={[styles.box, animatedStyle]} />
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  box: {
    width: 100,
    height: 100,
    backgroundColor: 'blue',
    borderRadius: 10,
  },
});
```

### 5. Bundle Size Optimization
Reduce JavaScript bundle size.

```json
{
  "name": "myapp",
  "dependencies": {
    "lodash": "^4.17.21",
    "date-fns": "^2.30.0"
  },
  "devDependencies": {
    "react-native-bundle-visualizer": "^3.0.0"
  },
  "scripts": {
    "analyze-bundle": "react-native-bundle-visualizer"
  }
}
```

```typescript
// Instead of importing the whole library
import _ from 'lodash'; // ❌

// Import only what you need
import debounce from 'lodash/debounce'; // ✅

// Or use modular imports
import { format } from 'date-fns'; // ✅
```

### 6. Startup Optimization
Improve app startup time.

```tsx
import React, { useEffect, useState } from 'react';
import { View, Text, ActivityIndicator } from 'react-native';
import AppNavigation from './AppNavigation';

// Defer non-critical initialization
function initializeNonCritical() {
  setTimeout(() => {
    // Initialize analytics
    // Initialize crash reporting
    // Load fonts asynchronously
  }, 1000);
}

export default function App() {
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    async function loadApp() {
      // Load only critical resources first
      await Promise.all([
        // Load essential fonts
        // Initialize essential services
      ]);
      
      setIsReady(true);
      
      // Defer non-critical
      initializeNonCritical();
    }
    
    loadApp();
  }, []);

  if (!isReady) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  return <AppNavigation />;
}
```

### 7. Memory Leak Prevention
Prevent common memory leaks.

```tsx
import React, { useState, useEffect, useRef } from 'react';
import { View, Text } from 'react-native';

export default function MemorySafeComponent() {
  const [data, setData] = useState(null);
  const isMounted = useRef(true);

  useEffect(() => {
    isMounted.current = true;
    
    const fetchData = async () => {
      const response = await fetch('https://api.example.com/data');
      const json = await response.json();
      
      // Check if component is still mounted
      if (isMounted.current) {
        setData(json);
      }
    };
    
    fetchData();
    
    const interval = setInterval(() => {
      console.log('Interval running');
    }, 1000);
    
    // Cleanup
    return () => {
      isMounted.current = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <View>
      <Text>{data ? JSON.stringify(data) : 'Loading...'}</Text>
    </View>
  );
}
```

## Best Practices
- **Use React.memo**: Memoize pure components
- **useMemo/useCallback**: Memoize expensive calculations and callbacks
- **Avoid Inline Styles**: Use StyleSheet.create for styles
- **Optimize FlatList**: Use proper FlatList configuration
- **Reanimated**: Use react-native-reanimated for animations
- **FastImage**: Use FastImage for better image handling
- **Analyze Bundle**: Check bundle size regularly
- **Hermes**: Enable Hermes engine for better performance
- **Profiling**: Use Flipper or React DevTools to profile
- **Defer Loading**: Load non-critical resources later
