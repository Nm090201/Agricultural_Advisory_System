def generate_simple_checklist(program):
    """Generate a simple application checklist"""
    
    checklist_text = f"""## Application Checklist for {program.get('program_name')}

### ✅ Before You Start
- [ ] Read full program details at: {program.get('official_url')}
- [ ] Check deadline: {program.get('application_deadlines')}
- [ ] Confirm you meet eligibility requirements

### 📋 Required Documents
"""
    
    for doc in program.get('required_documents', []):
        checklist_text += f"- [ ] {doc}\n"
    
    checklist_text += f"""
### 📞 Contact Information
If you have questions, contact: {program.get('contact_info')}

### 🚀 Next Steps
1. Gather all required documents
2. Contact your local office for guidance
3. Submit application via: {program.get('application_method')}

### 💡 Eligibility Requirements
"""
    
    for req in program.get('eligibility', []):
        checklist_text += f"- {req}\n"
    
    return checklist_text