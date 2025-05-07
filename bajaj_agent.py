import requests
import json
import re
from typing import Dict, Any

class BajajInsuranceAgent:
    """
    AI agent for extracting insurance information from Bajaj Allianz policy documents.
    
    This agent connects to the LNT chatservice API to extract structured information
    from Bajaj Allianz insurance policy documents using AI.
    """
    
    def __init__(self, bearer_token: str, base_url: str = "https://lntcs.ai/chatservice/chat"):
        """
        Initialize the Bajaj Allianz insurance extraction agent.
        
        Args:
            bearer_token: Authentication token for the API
            base_url: Base URL for the chat service API
        """
        self.bearer_token = bearer_token
        self.base_url = base_url
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {bearer_token}',
            'accept': 'application/json'
        }
    
    def create_extraction_prompt(self) -> str:
        """
        Create a specialized extraction prompt for Bajaj Allianz insurance policies.
            
        Returns:
            A detailed prompt for extracting insurance information
        """
        return """
          I need you to carefully extract specific insurance information from the Bajaj Allianz General Insurance policy document. 
          Focus ONLY on extracting the exact values for each item listed below.
  
          For each item, provide ONLY the value with no extra explanation:
  
          ## Basic Policy Information
          - Insured Name: [Extract the insured name, e.g., "LARSEN & TOUBRO LIMITED"]
          - Job No: [Extract the job number, e.g., "LE24M757"]
          - Risk Location: [Extract the exact risk location]
          - Project Description: [Extract the project description in detail]
          - Project Period: [Extract project period in months, e.g., "36 Months"]
          - Sum Insured: [Extract the total sum insured value]
          - Premium before tax: [Extract premium before tax]
          - GST amount: [Extract GST amount]
          - Final Premium: [Extract final premium amount]
  
          ## Sum Insured Breakup
          - Contract Price: [Extract the contract price]
          - Additional sum to cover: [Extract additional sum covered]
          - Materials supplied by Principal: [Extract value]
          - Temporary works: [Extract value]
          - Office Furniture and Equipment: [Extract value]
          - Contractor's own materials: [Extract value]
          - Contractor's Tools & tackles: [Extract value]
          - Overall Value of Sum Insured: [Extract the total value]
  
          ## Excess/Deductible Information
          - For Major Bridges/Works in water (Normal claims): [Extract excess details]
          - For Major Bridges/Works in water (AOG/Major Perils): [Extract excess details]
          - For Major Bridges/Works in water (Design Defects): [Extract excess details]
          - For All Other Works (Normal Claims): [Extract excess details]
          - For All Other Works (AOG/Major Perils): [Extract excess details]
          - For All Other Works (Design Defects): [Extract excess details]
          - Third Party Property Damage: [Extract excess details]
          - Bodily Injury Excess: [Extract excess details]
  
          ## Add-on Covers
          - Earthquake & STFI: [Extract coverage details]
          - Escalation: [Extract details]
          - Removal of debris: [Extract details]
          - Owners Surrounding Property: [Extract details]
          - Third Party Liability: [Extract details]
          - Design Defect Cover: [Extract design defect coverage details]
          - Waiver of Subrogation: [Extract waiver details]
          - Cover for offsite storage/fabrication: [Extract details]
          - Extended maintenance cover: [Extract details]
          - Plans and documents: [Extract details]
          - Put to use clause: [Extract details]
          - Cessation of works: [Extract details]
          - 50/50 clause: [Extract details]
          - 72 hrs. Clause: [Extract details]
          - Free Automatic Reinstatement Clause: [Extract details]
          - Professional Fees: [Extract details]
          - Claims preparation cost: [Extract details]
          - Internal shifting: [Extract details]
          - Waiver of Contribution Clause: [Extract details]
          - Additional Customs Duty: [Extract details]
          - Expediting Cost Including Air Freight: [Extract details]
          - Loss Minimization Expenses: [Extract details]
          - Temporary Repairs Clause: [Extract details]
          - Improvement cost: [Extract details]
          - Public Authorities clause: [Extract details]
          - Special conditions concerning piling foundation: [Extract details]
          - Special conditions concerning safety measures: [Extract details]
          - Special conditions concerning underground cables: [Extract details]
          - Special conditions concerning fire-fighting facilities: [Extract details]
          - Return period for coffer dam: [Extract details]
          - Endorsement concerning storage: [Extract details]
          - Endorsement for Temporary access roads: [Extract details]
          - Dewatering endorsement: [Extract details]
          
          ## Special Conditions and Warranties
          - Section Warranty for road projects: [Extract the full warranty text]
          - Territory and Jurisdiction: [Extract details]
          - Capacity: [Extract details]
          - Validity of Quote/Terms: [Extract details]
        """
    
    def extract_data(self, space_name: str, flow_name: str, document_name: str = "Bajaj-CAR-policy.pdf") -> Dict[str, Any]:
        """
        Extract insurance data from Bajaj Allianz policy document.
        
        Args:
            space_name: The space name for the API
            flow_name: The flow name for the API
            document_name: The name of the document to extract from (optional)
            
        Returns:
            Processed insurance data
        """
        print(f"Extracting data from Bajaj Allianz Insurance document: {document_name}...")
        
        extraction_prompt = self.create_extraction_prompt()
        
        # Create request payload
        payload = {
            "query": extraction_prompt,
            "space_name": space_name,
            "userId": "anonymous",
            "hint": "For the Bajaj Allianz document, look for exact phrases, headings, and tables that contain the insurance details. Pay special attention to sections labeled as \"Add-on Covers\", \"Scope of Cover and Details of Sum Insured\", \"Deductible\", and similar headings. Extract verbatim values where available - exact numbers, limits, and conditions as written in the document. Look for tables that show the Sum Insured breakup.",
            "flow_name": flow_name,
            "embedding_metadata": {
                "file_name": document_name
            }
        }
        
        try:
            # Make the API request
            response = requests.post(
                self.base_url,
                headers=self.headers,
                data=json.dumps(payload)
            )
            
            # Check if the request was successful
            response.raise_for_status()
            
            # Parse the response
            extraction_data = response.json()
            response_text = extraction_data.get("response", "")
            
            # Process the extracted data
            processed_data = self._process_extracted_text(response_text)
            return processed_data
            
        except requests.exceptions.RequestException as e:
            print(f"Error extracting data from Bajaj Allianz policy: {str(e)}")
            return {
                "insurer": "Bajaj Allianz",
                "error": str(e),
                "basicInfo": {},
                "coverages": {},
                "sumInsuredBreakup": {},
                "addOns": {},
                "excess": {},
                "warranties": []
            }
    
    def _process_extracted_text(self, response_text: str) -> Dict[str, Any]:
        """
        Process the extracted text response into structured data.
        
        Args:
            response_text: Raw text response from the API
            
        Returns:
            Structured insurance data
        """
        processed_data = {
            "insurer": "Bajaj Allianz",
            "basicInfo": {},
            "sumInsuredBreakup": {},
            "coverages": {},
            "addOns": {},
            "excess": {},
            "warranties": []
        }
        
        # Map for basic policy information extraction
        basic_info_mapping = {
            'Insured Name': ['Insured Name:', 'Insured Name', 'Insured:'],
            'Job No': ['Job No:', 'Job No.:', 'Job No'],
            'Risk Location': ['Risk Location:', 'Location:', 'Location'],
            'Project Description': ['Project Description:', 'Description of Project:', 'Project Description'],
            'Project Period': ['Project Period:', 'Project period:', 'Project period'],
            'Sum Insured': ['Sum Insured:', 'Overall Value of Sum Insured', 'Sum Insured'],
            'Premium (before tax)': ['Premium before tax:', 'CAR Premium Payable', 'Premium Before Tax'],
            'GST amount': ['GST amount:', 'GST:', 'GST @'],
            'Final Premium': ['Final Premium:', 'Final Premium', 'Total Premium']
        }
        
        # Extract basic policy information
        for key, possible_labels in basic_info_mapping.items():
            value = 'Not Found'
            
            for label in possible_labels:
                # Try to find the value using various patterns
                for pattern_str in [
                    f"{label}[\\s\\:\\-]+(.*?)(?=[\\n\\r]|$)",
                    f"{label}[\\s\\:\\-]+([\\d\\,\\.\\s\\+\\-Rs\\/INR]+)(?=[\\n\\r]|$)",
                    f"\\b{label}\\b[\\s\\:\\-]+([^\\n]+)"
                ]:
                    pattern = re.compile(pattern_str, re.IGNORECASE)
                    match = pattern.search(response_text)
                    if match and match.group(1) and match.group(1).strip():
                        value = match.group(1).strip()
                        break
                
                if value != 'Not Found':
                    break
            
            processed_data["basicInfo"][key] = value
        
        # Map for sum insured breakup information
        sum_insured_mapping = {
            'Contract Price': ['Contract Price:', 'Contract Price of', 'Contract Price'],
            'Additional sum to cover': ['Additional sum to cover:', 'Additional sum to cover'],
            'Materials supplied by Principal': ['Materials supplied by Principal:', 'Materials or items supplied by the Principal'],
            'Temporary works': ['Temporary works:', 'All kind of temporary works'],
            'Office Furniture and Equipment': ['Office Furniture:', 'Office Furniture, Fixtures'],
            'Contractor\'s own materials': ['Contractor\'s own materials:', 'Contractor\'s own materials'],
            'Contractor\'s Tools & tackles': ['Contractor\'s Tools & tackles:', 'Contractor\'s Tools & tackles'],
            'Overall Value of Sum Insured': ['Overall Value of Sum Insured:', 'Overall Value of Sum Insured']
        }
        
        # Extract sum insured breakup details
        for key, possible_labels in sum_insured_mapping.items():
            value = 'Not Found'
            
            for label in possible_labels:
                pattern = re.compile(f".*?{label}.*?(\\d[\\d\\,\\.\\s]+)", re.IGNORECASE)
                match = pattern.search(response_text)
                if match and match.group(1) and match.group(1).strip():
                    value = match.group(1).strip()
                    break
            
            processed_data["sumInsuredBreakup"][key] = value
        
        # Map for excess/deductible information
        excess_mapping = {
            'Major Bridges/Works - Normal Claims': ['For Major Bridges/Works in water.*?Normal claims.*?(\\d.*?)(?=\\n|$)', 'Major Bridges/Works.*?Normal.*?(\\d.*?)(?=\\n|$)'],
            'Major Bridges/Works - AOG/Major Perils': ['For Major Bridges/Works in water.*?AOG/Major Perils.*?(\\d.*?)(?=\\n|$)', 'Major Bridges/Works.*?AOG.*?(\\d.*?)(?=\\n|$)'],
            'Major Bridges/Works - Design Defects': ['For Major Bridges/Works in water.*?Design Defects.*?(\\d.*?)(?=\\n|$)', 'Design Defects.*?Major Bridges.*?(\\d.*?)(?=\\n|$)'],
            'All Other Works - Normal Claims': ['For All Other Works.*?Normal Claims.*?(\\d.*?)(?=\\n|$)', 'Other Works.*?Normal.*?(\\d.*?)(?=\\n|$)'],
            'All Other Works - AOG/Major Perils': ['For All Other Works.*?AOG/Major Perils.*?(\\d.*?)(?=\\n|$)', 'Other Works.*?AOG.*?(\\d.*?)(?=\\n|$)'],
            'All Other Works - Design Defects': ['For All Other Works.*?Design Defects.*?(\\d.*?)(?=\\n|$)', 'Design Defects.*?Other Works.*?(\\d.*?)(?=\\n|$)'],
            'Third Party Property Damage': ['Third Party Property Damage.*?(\\d.*?)(?=\\n|$)', 'Property damage.*?(\\d.*?)(?=\\n|$)'],
            'Bodily Injury': ['Bodily injury.*?(\\d.*?)(?=\\n|$)', 'For Bodily injury.*?(\\d.*?)(?=\\n|$)']
        }
        
        # Extract excess/deductible information
        for key, pattern_list in excess_mapping.items():
            value = 'Not Found'
            
            for pattern_str in pattern_list:
                pattern = re.compile(pattern_str, re.IGNORECASE | re.DOTALL)
                match = pattern.search(response_text)
                if match and match.group(1) and match.group(1).strip():
                    value = match.group(1).strip()
                    break
            
            processed_data["excess"][key] = value
        
        # Map for add-on covers
        add_on_mapping = {
            'Earthquake & STFI': ['Cover for Earthquake', 'Earthquake \\(Fire & Shock\\) & STFI'],
            'Escalation': ['Escalation', 'Escalation – up to'],
            'Removal of debris': ['Removal of debris', 'Removal of debris \\(including Dewatering'],
            'Owners Surrounding Property': ['Owners Surrounding Property', 'Owners Surrounding Property with FLEXA'],
            'Third Party Liability': ['Third Party Liability', 'Third Party Liability with cross'],
            'Design Defect Cover': ['Design Defect Cover', 'Design Defect Cover as per'],
            'Waiver of Subrogation': ['Waiver of Subrogation', 'Waiver of Subrogation Clause'],
            'Cover for offsite storage': ['Cover for offsite storage', 'offsite storage/fabrication'],
            'Extended maintenance cover': ['Extended maintenance cover', 'Extended maintenance'],
            'Plans and documents': ['Plans and documents', 'Plans and documents up to'],
            'Put to use clause': ['Put to use clause', 'Put to use'],
            'Cessation of works': ['Cessation of works', 'Cessation of works up to'],
            '50/50 clause': ['50/50 clause', '50/50'],
            '72 hrs. Clause': ['72 hrs. Clause', '72 hrs'],
            'Free Automatic Reinstatement': ['Free Automatic Reinstatement', 'Free Automatic Reinstatement Clause'],
            'Professional Fees': ['Professional Fees', 'Cover for Professional Fees'],
            'Claims preparation cost': ['Claims preparation cost', 'Claims preparation'],
            'Internal shifting': ['Internal shifting', 'Internal shifting of project'],
            'Waiver of Contribution Clause': ['Waiver of Contribution', 'Waiver of Contribution Clause'],
            'Additional Customs Duty': ['Additional Customs Duty', 'Additional Customs'],
            'Expediting Cost': ['Expediting Cost', 'Expediting Cost Including Air Freight'],
            'Loss Minimization Expenses': ['Loss Minimization Expenses', 'Loss Minimization'],
            'Temporary Repairs Clause': ['Temporary Repairs Clause', 'Temporary Repairs'],
            'Improvement cost': ['Improvement cost', 'Improvement cost actual'],
            'Public Authorities clause': ['Public Authorities clause', 'Public Authorities'],
            'Special conditions for piling': ['Special conditions concerning piling', 'piling foundation'],
            'Safety measures': ['Special conditions concerning safety', 'safety measures'],
            'Underground cables': ['Special conditions concerning underground', 'underground cables'],
            'Fire-fighting facilities': ['Special conditions concerning fire-fighting', 'fire-fighting facilities'],
            'Coffer dam': ['Return period for coffer dam', 'coffer dam'],
            'Storage': ['Endorsement concerning storage', 'storage'],
            'Temporary access roads': ['Endorsement for Temporary access', 'Temporary access roads'],
            'Dewatering': ['Dewatering endorsement', 'Dewatering']
        }
        
        # Extract add-on covers
        for key, possible_patterns in add_on_mapping.items():
            value = 'Not Found'
            
            # Try to match coverage information after the pattern
            for pattern_base in possible_patterns:
                pattern_str = f"{pattern_base}\\s*(?::|as per|up to|\\-)?\\s*(.*?)(?=\\s*•|\\s*\\n\\s*[A-Z]|$)"
                pattern = re.compile(pattern_str, re.IGNORECASE | re.DOTALL)
                match = pattern.search(response_text)
                
                if match and match.group(1) and match.group(1).strip():
                    value = match.group(1).strip()
                    break
                
                # If detailed match not found, check if add-on is at least mentioned
                simple_pattern = re.compile(f"{pattern_base}", re.IGNORECASE)
                if simple_pattern.search(response_text):
                    value = 'Included'
                    break
            
            processed_data["addOns"][key] = value
        
        # Extract special conditions and warranties
        warranty_section = re.search(r"Section Warranty for road projects:.*?(It is hereby agreed.*?)(?=Territory and Jurisdiction|$)", response_text, re.DOTALL | re.IGNORECASE)
        if warranty_section:
            warranty_text = warranty_section.group(1).strip()
            processed_data["warranties"].append({
                "title": "Section Warranty for road projects",
                "content": warranty_text
            })
        
        # Extract territory information
        territory_match = re.search(r"Territory and Jurisdiction:\s*(.*?)(?=\n|$)", response_text, re.IGNORECASE)
        if territory_match:
            processed_data["basicInfo"]["Territory and Jurisdiction"] = territory_match.group(1).strip()
        
        # Extract capacity information
        capacity_match = re.search(r"Capacity:\s*(.*?)(?=\n|$)", response_text, re.IGNORECASE)
        if capacity_match:
            processed_data["basicInfo"]["Capacity"] = capacity_match.group(1).strip()
        
        # Extract validity of quote
        validity_match = re.search(r"Validity of Quote/Terms:\s*(.*?)(?=\n|$)", response_text, re.IGNORECASE)
        if validity_match:
            processed_data["basicInfo"]["Validity of Quote"] = validity_match.group(1).strip()
        
        return processed_data