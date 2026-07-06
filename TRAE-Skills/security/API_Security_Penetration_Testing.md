# Skill: API Security Penetration Testing

## Purpose
To systematically test APIs for security vulnerabilities, following OWASP guidelines and industry best practices.

## When to Use
- Before deploying a new API to production
- After making significant changes to API endpoints
- As part of regular security audits
- When implementing a security compliance program (SOC2, ISO27001)
- After discovering a security breach or vulnerability

## Procedure

### 1. Information Gathering
Collect information about the API.

```bash
# Use curl to explore endpoints
curl -v https://api.example.com/v1/
curl -v https://api.example.com/v1/users

# Check for exposed documentation
curl https://api.example.com/swagger.json
curl https://api.example.com/docs
curl https://api.example.com/apidoc

# Use nmap to scan for open ports
nmap -p 443,8080,8443 api.example.com
```

### 2. Authentication & Authorization Testing
Test authentication and authorization mechanisms.

```bash
# Test missing authentication
curl https://api.example.com/v1/admin/users

# Test broken object level authorization (BOLA)
curl -H "Authorization: Bearer USER1_TOKEN" https://api.example.com/v1/users/2

# Test weak tokens
# Check if JWT tokens are using weak algorithms (none, HS256 with weak secrets)
# Try to tamper with JWT payload
```

### 3. Injection Attacks
Test for SQL injection, NoSQL injection, and other injection vulnerabilities.

```bash
# SQL Injection test
curl "https://api.example.com/v1/users?id=1' OR '1'='1"
curl "https://api.example.com/v1/users?id=1'; DROP TABLE users;--"

# NoSQL Injection test
curl -X POST https://api.example.com/v1/login \
  -H "Content-Type: application/json" \
  -d '{"username": {"$ne": null}, "password": {"$ne": null}}'

# Command Injection test
curl "https://api.example.com/v1/convert?file=test.jpg; ls -la"
```

### 4. Rate Limiting & DoS Testing
Test if rate limiting is properly implemented.

```bash
# Use ab (Apache Bench) for load testing
ab -n 1000 -c 100 https://api.example.com/v1/

# Use curl in a loop
for i in {1..1000}; do
  curl https://api.example.com/v1/ &
done
wait
```

### 5. Using OWASP ZAP
Automated security testing with OWASP ZAP.

```bash
# Run ZAP in headless mode
zap.sh -daemon -host 0.0.0.0 -port 8080 -config api.addrs.addr.name=.* -config api.addrs.addr.regex=true -config api.key=your-api-key

# Run an active scan
curl "http://localhost:8080/JSON/ascan/action/scan/?apikey=your-api-key&url=https://api.example.com&recurse=true"
```

## Best Practices
- **OWASP Top 10**: Focus on OWASP API Security Top 10 vulnerabilities
- **Automated + Manual**: Use both automated tools and manual testing
- **Test Environment**: Always test in a staging environment, not production
- **Documentation**: Document all findings and remediation steps
- **Prioritization**: Prioritize vulnerabilities by severity and exploitability
- **Remediation Verification**: Re-test after fixes are applied
- **Regular Testing**: Perform security testing regularly (quarterly, after major changes)
