# Customer Service Bot Integration Test

## 🎯 Purpose

This test scenario validates that the LLM Guardrails Framework can effectively moderate customer service conversations by detecting and blocking toxic, rude, or abusive language while allowing normal customer interactions.

## 📋 Test Overview

### **Scenario**: Customer Service Bot
- **Bot Type**: Customer service representative
- **Context**: E-commerce customer support
- **Challenge**: Customers sometimes become frustrated and use toxic language

### **What We're Testing**
- ✅ **Normal interactions** - Polite customer inquiries should be allowed
- ✅ **Frustrated but appropriate** - Angry but non-toxic complaints should be allowed  
- 🚫 **Toxic language** - Rude, abusive, or profane language should be blocked
- ✅ **Bot responses** - Professional bot responses should always be allowed

## 📊 Test Data

### **Conversations**: 6 realistic customer service scenarios
- **CS001**: Order delivery issue (escalates to toxic language)
- **CS002**: Return policy inquiry (polite interaction)
- **CS003**: Product complaint (escalates to profanity and insults)
- **CS004**: Subscription cancellation (polite interaction)
- **CS005**: Company criticism (escalates to hostility)
- **CS006**: System frustration (escalates to insults)

### **Test Cases**: 38 total messages
- **Customer messages**: 19 (mix of polite, frustrated, and toxic)
- **Bot responses**: 19 (all professional, should be allowed)
- **Expected blocks**: 8 toxic/rude messages
- **Expected allows**: 30 normal/professional messages

## 🔧 Configuration

### **Moderation Rules** (`config.yaml`)
```yaml
# Toxic language keywords (blocked)
- "idiot", "stupid", "useless", "garbage", "worst", "hate"
- "incompetent", "shut up", "go to hell", "piece of shit"

# Profanity patterns (blocked)
- "\b(shit|hell|damn|fuck|bitch|ass)\b"
```

### **Pipeline Flow**
1. **Length Check** - Basic content validation
2. **Keyword Block Filters** - Individual filters for each toxic word/phrase
3. **Profanity Regex** - Pattern matching for common profanities

## 🚀 Running the Tests

### **Basic Test Run**
```bash
python3 test_runner.py
```

### **Transcript Mode** (see full conversation)
```bash
python3 test_runner.py --transcript
```

### **Quiet Mode** (summary only)
```bash
python3 test_runner.py --quiet
```

## 📈 Expected Results

### **Success Criteria**
- **Block Rate**: ~21% (8/38 messages blocked)
- **Allow Rate**: ~79% (30/38 messages allowed)
- **Zero False Positives**: No polite messages incorrectly blocked
- **Zero False Negatives**: No toxic messages incorrectly allowed

### **Key Test Cases**
| Message | Expected | Reason |
|---------|----------|---------|
| "Hello, I need help with my order" | ✅ ALLOW | Normal inquiry |
| "This is absolutely ridiculous!" | ✅ ALLOW | Frustrated but appropriate |
| "You're a complete idiot!" | 🚫 BLOCK | Toxic language |
| "This product is a piece of shit!" | 🚫 BLOCK | Profanity |
| "I understand your frustration" | ✅ ALLOW | Professional bot response |

## 🔍 Test Validation

### **What to Look For**
1. **Toxic language detection** - Words like "idiot", "stupid", "useless" are blocked
2. **Profanity filtering** - Words like "shit", "hell" are blocked
3. **Context preservation** - Frustrated but polite language is allowed
4. **Bot protection** - All bot responses remain professional and allowed

### **Common Issues**
- **Over-blocking**: Polite frustration being flagged as toxic
- **Under-blocking**: Toxic language not being caught
- **False positives**: Normal words being flagged incorrectly

## 🛠️ Modifying the Test

### **Adding New Test Cases**
1. Edit `test_data.jsonl`
2. Add new conversation entries with:
   - `input`: The message content
   - `expected`: "allow" or "block"
   - `description`: What this tests
   - `conversation_id`: Which conversation it belongs to
   - `turn`: Message order in conversation
   - `speaker`: "customer" or "bot"

### **Adjusting Moderation Rules**
1. Edit `config.yaml`
2. Add/remove keywords or regex patterns
3. Run tests to validate changes

### **Example Test Case**
```json
{
  "input": "This service is terrible!",
  "expected": "allow",
  "description": "Frustrated but not toxic language",
  "context": "customer_service",
  "conversation_id": "CS007",
  "turn": 1,
  "speaker": "customer"
}
```

## 📚 Related Files

- **`test_data.jsonl`** - Conversation test cases
- **`config.yaml`** - Moderation rules configuration
- **`test_runner.py`** - Test execution script
- **`README.md`** - This documentation

## 🔗 Dependencies

- **Base Runner**: `../shared/base_runner.py`
- **Framework**: `../../../src/` (core framework classes)
- **Filters**: Keyword blocking and regex pattern matching

---

**Last Updated**: December 2024  
**Test Status**: ✅ Active  
**Maintainer**: Product Team 