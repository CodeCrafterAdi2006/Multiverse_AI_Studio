# Skill: Zero Trust Architecture Implementation

## Purpose
To implement a Zero Trust security model where no entity is trusted by default, requiring verification for every access request.

## When to Use
- When migrating to cloud environments
- For securing remote workforces
- When dealing with sensitive data
- After security breaches or incidents
- For compliance requirements (GDPR, HIPAA, etc.)

## Procedure

### 1. Identity Verification (MFA)
Implement strong multi-factor authentication.

```python
import pyotp
import qrcode

class MFASystem:
    def __init__(self):
        self.users = {}
    
    def enroll_user(self, user_id):
        secret = pyotp.random_base32()
        self.users[user_id] = secret
        
        # Generate QR code
        uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user_id,
            issuer_name="MyApp"
        )
        
        img = qrcode.make(uri)
        img.save(f"{user_id}_qrcode.png")
        
        return secret
    
    def verify_token(self, user_id, token):
        if user_id not in self.users:
            return False
        
        totp = pyotp.TOTP(self.users[user_id])
        return totp.verify(token)

# Usage
mfa = MFASystem()
secret = mfa.enroll_user("john.doe")
print("Scan QR code with authenticator app")

# Verify later
token = input("Enter 6-digit token: ")
if mfa.verify_token("john.doe", token):
    print("Authenticated!")
else:
    print("Invalid token")
```

### 2. JWT with Short Expiry and Refresh Tokens
Use short-lived JWTs with refresh tokens.

```javascript
import jwt from 'jsonwebtoken';

const ACCESS_TOKEN_SECRET = 'your-access-secret';
const REFRESH_TOKEN_SECRET = 'your-refresh-secret';
const ACCESS_TOKEN_EXPIRY = '15m';
const REFRESH_TOKEN_EXPIRY = '7d';

const refreshTokens = new Set();

function generateAccessToken(user) {
  return jwt.sign(
    { userId: user.id, email: user.email, role: user.role },
    ACCESS_TOKEN_SECRET,
    { expiresIn: ACCESS_TOKEN_EXPIRY }
  );
}

function generateRefreshToken(user) {
  const refreshToken = jwt.sign(
    { userId: user.id },
    REFRESH_TOKEN_SECRET,
    { expiresIn: REFRESH_TOKEN_EXPIRY }
  );
  refreshTokens.add(refreshToken);
  return refreshToken;
}

function authenticateToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];
  
  if (!token) return res.sendStatus(401);
  
  jwt.verify(token, ACCESS_TOKEN_SECRET, (err, user) => {
    if (err) return res.sendStatus(403);
    req.user = user;
    next();
  });
}

function refreshAccessToken(req, res) {
  const refreshToken = req.body.token;
  if (!refreshToken) return res.sendStatus(401);
  if (!refreshTokens.has(refreshToken)) return res.sendStatus(403);
  
  jwt.verify(refreshToken, REFRESH_TOKEN_SECRET, (err, user) => {
    if (err) return res.sendStatus(403);
    
    const accessToken = generateAccessToken(user);
    res.json({ accessToken });
  });
}
```

### 3. Micro-Segmentation with Network Policies
Implement network segmentation in Kubernetes.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-ingress
spec:
  podSelector: {}
  policyTypes:
  - Ingress
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-api
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-api-to-database
spec:
  podSelector:
    matchLabels:
      app: database
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: api
    ports:
    - protocol: TCP
      port: 5432
```

### 4. Continuous Verification with Risk-Based Authentication
Implement risk scoring for authentication.

```javascript
function calculateRiskScore(req) {
  let score = 0;
  
  // Check IP reputation
  if (isHighRiskIP(req.ip)) score += 30;
  
  // Check device fingerprint
  if (!isRecognizedDevice(req)) score += 25;
  
  // Check location
  if (isUnusualLocation(req)) score += 20;
  
  // Check time of day
  if (isUnusualTime(req)) score += 15;
  
  // Check request rate
  if (exceedsRateLimit(req)) score += 10;
  
  return score;
}

function authenticateWithRisk(req, res, next) {
  const riskScore = calculateRiskScore(req);
  
  if (riskScore >= 70) {
    // Require step-up authentication
    return res.status(401).json({ requireStepUp: true, method: 'webauthn' });
  } else if (riskScore >= 40) {
    // Require MFA
    return res.status(401).json({ requireStepUp: true, method: 'mfa' });
  } else if (riskScore >= 20) {
    // Verify with device cookie
    if (!hasValidDeviceCookie(req)) {
      return res.status(401).json({ requireStepUp: true, method: 'email' });
    }
  }
  
  // Low risk, proceed
  next();
}
```

### 5. Least Privilege Access Control
Implement fine-grained authorization.

```javascript
const policies = {
  user: {
    can: [
      { resource: 'profile', action: ['read', 'update'] },
      { resource: 'own_data', action: ['read', 'write', 'delete'] }
    ]
  },
  admin: {
    can: [
      { resource: '*', action: '*' }
    ]
  },
  manager: {
    can: [
      { resource: 'profile', action: ['read', 'update'] },
      { resource: 'team_data', action: ['read', 'write'] }
    ],
    inherits: ['user']
  }
};

function checkPermission(userRole, resource, action) {
  const role = policies[userRole];
  if (!role) return false;
  
  // Check direct permissions
  for (const permission of role.can) {
    if (permission.resource === '*' && permission.action === '*') {
      return true;
    }
    if ((permission.resource === resource || permission.resource === '*') &&
        (permission.action.includes(action) || permission.action === '*')) {
      return true;
    }
  }
  
  // Check inherited permissions
  if (role.inherits) {
    for (const inheritedRole of role.inherits) {
      if (checkPermission(inheritedRole, resource, action)) {
        return true;
      }
    }
  }
  
  return false;
}

// Middleware
function authorize(resource, action) {
  return (req, res, next) => {
    if (checkPermission(req.user.role, resource, action)) {
      next();
    } else {
      res.sendStatus(403);
    }
  };
}

// Usage
app.get('/api/data', authorize('team_data', 'read'), (req, res) => {
  res.json({ data: 'sensitive data' });
});
```

## Best Practices
- **Verify Explicitly**: Never trust, always verify
- **Least Privilege**: Grant minimal permissions needed
- **Assume Breach**: Operate as if breach has already occurred
- **Continuous Monitoring**: Log and monitor everything
- **MFA Everywhere**: Require MFA for all access
- **Micro-Segmentation**: Segment networks and limit lateral movement
- **Encrypt Everything**: Encrypt data in transit and at rest
- **Regular Audits**: Audit access logs and permissions regularly
