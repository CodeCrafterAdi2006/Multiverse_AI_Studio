# Skill: Password Hashing (Argon2 / BCrypt)

## Purpose
To securely store user passwords in a database so that even if the data is breached, attackers cannot easily recover the original passwords. Hashing is a one-way mathematical function that converts a password into a unique string of characters.

## When to Use
- When building a custom user authentication system
- When storing any sensitive secrets (e.g., API keys, PINs) that don't need to be decrypted
- When migrating from older, insecure hashing methods (like MD5 or SHA1)

## Procedure

### 1. The Right Algorithm: Argon2
[Argon2](https://github.com/P-H-C/phc-winner-argon2) is the winner of the Password Hashing Competition (PHC) and is the current industry gold standard. It's memory-hard and time-hard, making it extremely resistant to GPU/ASIC-based brute-force attacks.

**Installation (Node.js)**:
```bash
npm install argon2
```

**Implementation**:
```javascript
const argon2 = require('argon2');

// 1. Hashing a password
async function signup(password) {
  // Argon2 automatically generates a unique Salt for every password
  const hashedPassword = await argon2.hash(password, {
    type: argon2.argon2id, // Recommended hybrid mode
    memoryCost: 2 ** 16,   // 64MB (Memory-hardness)
    timeCost: 3,           // 3 iterations (Time-hardness)
    parallelism: 1         // Number of threads
  });
  
  // Store hashedPassword in your database
  await db.users.create({ password: hashedPassword });
}

// 2. Verifying a password during login
async function login(username, inputPassword) {
  const user = await db.users.findUnique({ where: { username } });
  
  // argon2.verify(hashedPassword, plainPassword)
  const isMatch = await argon2.verify(user.password, inputPassword);
  
  if (isMatch) {
    // Generate JWT/Session
  } else {
    // Invalid credentials
  }
}
```

### 2. The Reliable Alternative: BCrypt
BCrypt is a mature, widely used algorithm. While older than Argon2, it's still very secure for most applications.

**Installation (Node.js)**:
```bash
npm install bcrypt
```

**Implementation**:
```javascript
const bcrypt = require('bcrypt');

// 1. Hashing
const saltRounds = 12; // "Cost factor" - determines how slow the hash is
const hashedPassword = await bcrypt.hash(password, saltRounds);

// 2. Verifying
const isMatch = await bcrypt.compare(inputPassword, hashedPassword);
```

### 3. Salting (Automatic)
Both Argon2 and BCrypt handle **Salting** automatically. A salt is a random string added to the password *before* hashing. This ensures that even if two users have the same password ("123456"), their stored hashes will be completely different, preventing "Rainbow Table" attacks.

## Best Practices
- **Never use MD5, SHA1, or SHA256**: These are too fast. Modern GPUs can calculate billions of SHA256 hashes per second, making them easy to brute-force.
- **Tune for Performance**: A password hash should take between 100ms and 500ms on your server. This is unnoticeable to a user but makes it incredibly expensive for an attacker to try millions of combinations.
- **Store the entire hash string**: Argon2 and BCrypt hashes include the algorithm version, cost parameters, salt, and the hash itself in a single string (e.g., `$argon2id$v=19$m=65536,t=3,p=4$...`). Store this entire string in a `VARCHAR` column in your database.
- **Update Cost Factors**: As hardware gets faster, you may need to increase your `memoryCost` or `saltRounds`. When a user logs in, check if their hash uses an old cost factor and re-hash it if necessary.
- **Pepper (Optional but Good)**: A "Pepper" is a secret key stored in your application's environment variables (not in the database). It's added to every password before hashing. If the database is breached but the environment variables are safe, the hashes are much harder to crack.