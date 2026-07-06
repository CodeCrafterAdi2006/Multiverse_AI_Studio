# Skill: Advanced WebGL with Three.js

## Purpose
To build high-performance 3D graphics, animations, and interactive experiences using Three.js, including shaders, post-processing, and advanced rendering techniques.

## When to Use
- When building 3D product configurators or visualizers
- For creating interactive data visualizations in 3D
- When developing games or game-like experiences for the web
- For building virtual tours or architectural visualizations
- When implementing advanced particle effects or simulations

## Procedure

### 1. Custom Shaders (GLSL)
Create custom vertex and fragment shaders.

```javascript
import * as THREE from 'three';

const vertexShader = `
  varying vec2 vUv;
  varying vec3 vPosition;
  
  void main() {
    vUv = uv;
    vPosition = position;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;

const fragmentShader = `
  varying vec2 vUv;
  varying vec3 vPosition;
  uniform float time;
  
  void main() {
    vec3 color = 0.5 + 0.5 * cos(time + vPosition.xyx + vec3(0.0, 2.0, 4.0));
    gl_FragColor = vec4(color, 1.0);
  }
`;

const material = new THREE.ShaderMaterial({
  vertexShader,
  fragmentShader,
  uniforms: {
    time: { value: 0 }
  }
});

const geometry = new THREE.BoxGeometry(1, 1, 1);
const mesh = new THREE.Mesh(geometry, material);
scene.add(mesh);

// Animate
function animate() {
  requestAnimationFrame(animate);
  material.uniforms.time.value += 0.01;
  renderer.render(scene, camera);
}
```

### 2. Post-Processing Effects
Use post-processing for bloom, depth of field, and other effects.

```javascript
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';

const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));

const bloomPass = new UnrealBloomPass(
  new THREE.Vector2(window.innerWidth, window.innerHeight),
  1.5, // strength
  0.4, // radius
  0.85 // threshold
);
composer.addPass(bloomPass);

// Animate with composer
function animate() {
  requestAnimationFrame(animate);
  composer.render();
}
```

### 3. Particle Systems
Create advanced particle effects.

```javascript
const particleCount = 10000;
const positions = new Float32Array(particleCount * 3);
const colors = new Float32Array(particleCount * 3);

for (let i = 0; i < particleCount; i++) {
  positions[i * 3] = (Math.random() - 0.5) * 10;
  positions[i * 3 + 1] = (Math.random() - 0.5) * 10;
  positions[i * 3 + 2] = (Math.random() - 0.5) * 10;
  
  colors[i * 3] = Math.random();
  colors[i * 3 + 1] = Math.random();
  colors[i * 3 + 2] = Math.random();
}

const geometry = new THREE.BufferGeometry();
geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

const material = new THREE.PointsMaterial({
  size: 0.02,
  vertexColors: true
});

const particles = new THREE.Points(geometry, material);
scene.add(particles);
```

### 4. Physics Integration (Cannon.js)
Add physics to your 3D scene.

```javascript
import * as CANNON from 'cannon-es';

const world = new CANNON.World({
  gravity: new CANNON.Vec3(0, -9.82, 0)
});

// Create ground
const groundBody = new CANNON.Body({
  shape: new CANNON.Plane(),
  mass: 0
});
groundBody.quaternion.setFromAxisAngle(new CANNON.Vec3(1, 0, 0), -Math.PI / 2);
world.addBody(groundBody);

// Create falling sphere
const sphereBody = new CANNON.Body({
  mass: 5,
  shape: new CANNON.Sphere(0.5)
});
sphereBody.position.set(0, 5, 0);
world.addBody(sphereBody);

// Update physics in animation loop
function animate() {
  requestAnimationFrame(animate);
  world.step(1 / 60);
  
  // Sync Three.js mesh with physics body
  mesh.position.copy(sphereBody.position);
  mesh.quaternion.copy(sphereBody.quaternion);
  
  renderer.render(scene, camera);
}
```

## Best Practices
- **Performance**: Use BufferGeometry instead of Geometry for better performance
- **LOD**: Implement Level of Detail for distant objects
- **Textures**: Compress textures and use appropriate sizes
- **Memory**: Dispose of unused geometries, materials, and textures
- **Shaders**: Optimize shaders by minimizing expensive operations
- **Responsive**: Handle window resizing and device pixel ratio correctly
