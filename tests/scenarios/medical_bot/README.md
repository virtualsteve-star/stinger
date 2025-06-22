# Medical Bot Integration Test

## 🎯 Purpose

This test scenario validates that the LLM Guardrails Framework can effectively detect and flag Personally Identifiable Information (PII) in medical conversations while allowing normal healthcare interactions to proceed.

## 📋 Test Overview

### **Scenario**: Medical Bot
- **Bot Type**: Healthcare assistant/telemedicine bot
- **Context**: Medical consultations and health advice
- **Challenge**: Patients may inadvertently share sensitive personal information

### **What We're Testing**
- ✅ **Normal medical interactions** - Health questions and advice should be allowed
- ✅ **Symptom descriptions** - Medical symptoms and conditions should be allowed
- ⚠️ **PII detection** - Personal information should be flagged for review
- ✅ **Bot responses** - Professional medical responses should be allowed

## 📊 Test Data

### **Conversations**: 8 realistic medical scenarios
- **MED001**: Chest pain emergency (patient shares contact info)
- **MED002**: Medication interaction (patient shares doctor info)
- **MED003**: Fever and headache (patient shares insurance/DOB)
- **MED004**: Mental health support (patient shares address)
- **MED005**: Diabetes management (patient shares SSN)
- **MED006**: Prenatal care (patient shares medical record number)
- **MED007**: Allergic reaction (patient shares credit card)
- **MED008**: Prescription refill (patient shares prescription/email)

### **Test Cases**: 48 total messages
- **Patient messages**: 24 (mix of medical questions and PII sharing)
- **Bot responses**: 24 (all professional, should be allowed)
- **Expected warnings**: 8 PII-containing messages
- **Expected allows**: 40 normal medical messages

## 🔧 Configuration

### **PII Detection Rules** (`config.yaml`)
```yaml
# Personal Identifiable Information patterns (warned)
- SSN: "\b\d{3}-\d{2}-\d{4}\b"
- Credit Card: "\b\d{4}-\d{4}-\d{4}-\d{4}\b"
- Email: "\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
- Phone: "\b\d{3}-\d{3}-\d{4}\b"
- Full Names: "\b[A-Z][a-z]+\s+[A-Z][a-z]+\b"
- Date of Birth: "\b\d{1,2}/\d{1,2}/\d{4}\b"

# Medical identifiers (warned)
- Medical Records: "\b[A-Z]{2}-\d{6}\b"
- Prescriptions: "\bRX-\d{6}\b"
- Insurance: "\b\d{9}\b"
```

### **Pipeline Flow**
1. **Length Check** - Basic content validation
2. **PII Detection** - Regex patterns for personal information
3. **Medical Identifiers** - Healthcare-specific sensitive data

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
- **Warn Rate**: ~17% (8/48 messages warned for PII)
- **Allow Rate**: ~83% (40/48 messages allowed)
- **Zero False Positives**: No normal medical content incorrectly flagged
- **Zero False Negatives**: No PII incorrectly allowed through

### **Key Test Cases**
| Message | Expected | Reason |
|---------|----------|---------|
| "I have chest pain" | ✅ ALLOW | Normal medical inquiry |
| "My name is John Smith" | ⚠️ WARN | Contains full name |
| "My SSN is 123-45-6789" | ⚠️ WARN | Contains SSN |
| "I need help with my medication" | ✅ ALLOW | Normal medical question |
| "My credit card is 4111-1111-1111-1111" | ⚠️ WARN | Contains credit card |

## 🔍 Test Validation

### **What to Look For**
1. **PII detection** - Names, SSNs, credit cards, emails are flagged
2. **Medical privacy** - Medical record numbers, prescriptions are flagged
3. **Context preservation** - Medical symptoms and questions are allowed
4. **Bot protection** - All bot responses remain professional and allowed

### **Common Issues**
- **Over-flagging**: Normal medical terms being flagged as PII
- **Under-flagging**: PII not being detected correctly
- **False positives**: Medical terminology being flagged incorrectly

## 🛠️ Modifying the Test

### **Adding New Test Cases**
1. Edit `test_data.jsonl`
2. Add new conversation entries with:
   - `input`: The message content
   - `expected`: "allow" or "warn"
   - `description`: What this tests
   - `conversation_id`: Which conversation it belongs to
   - `turn`: Message order in conversation
   - `speaker`: "patient" or "bot"

### **Adjusting PII Detection Rules**
1. Edit `config.yaml`
2. Add/remove regex patterns for different PII types
3. Run tests to validate changes

### **Example Test Case**
```json
{
  "input": "My blood pressure is 140/90",
  "expected": "allow",
  "description": "Medical data without PII",
  "context": "medical",
  "conversation_id": "MED009",
  "turn": 1,
  "speaker": "patient"
}
```

## 🔒 Privacy Considerations

### **HIPAA Compliance**
- This test validates that PII is detected and flagged
- In production, flagged content should be reviewed by humans
- No PII should be stored or logged without proper safeguards

### **Data Handling**
- Test data uses fictional PII for validation
- Real PII should never be used in test scenarios
- All test data should be clearly marked as synthetic

## 📚 Related Files

- **`test_data.jsonl`** - Conversation test cases
- **`config.yaml`** - PII detection rules configuration
- **`test_runner.py`** - Test execution script
- **`README.md`** - This documentation

## 🔗 Dependencies

- **Base Runner**: `../shared/base_runner.py`
- **Framework**: `../../../src/` (core framework classes)
- **Filters**: Regex pattern matching for PII detection

---

**Last Updated**: December 2024  
**Test Status**: ✅ Active  
**Maintainer**: Product Team  
**Privacy Level**: High (PII detection testing) 