import requests
import json
import time
import os

API_URL = "http://localhost:8000/api/chat"

prompts = [
    # Dental Sector (15)
    "How can AI help my dental practice save time?",
    "What is the cost of a missed call in a dental office?",
    "Can you automate my dental insurance verification process?",
    "How do you handle patient recall automation?",
    "What is the benefit of digital intake for dentists?",
    "How does your AI integrate with dental practice management software?",
    "Can you help reduce our staff burnout?",
    "How do we recover lost revenue from canceled appointments?",
    "What specific ROI can a dental clinic expect from Zymnix?",
    "How do you handle HIPAA compliance in your automations?",
    "My dental team is overwhelmed. Where do we start with AI?",
    "How does a designer-quality website attract high-value dental patients?",
    "What is the Zymnix approach to dental SEO?",
    "Do you offer automated text-back for missed calls in clinics?",
    "How can AI help with patient treatment plan acceptance?",

    # Legal Sector (15)
    "How can AI revolutionize my law firm's workflow?",
    "What is the impact of automated eDiscovery on case outcomes?",
    "Can you automate legal billing for a mid-sized firm?",
    "How do you handle document review for thousands of contracts?",
    "What is compliance scoring and why does it matter?",
    "Can you generate case timelines automatically?",
    "How does AI reduce human error in legal filing?",
    "Can you integrate with Clio or MyCase?",
    "How do you ensure data security for sensitive legal documents?",
    "What is the ROI of AI for a personal injury law firm?",
    "How can AI help with intake and lead qualification for lawyers?",
    "Why is high-end UI important for a law firm's credibility?",
    "Can your AI help with legal research?",
    "How do you automate the collection of evidence for litigation?",
    "How do we stay ahead of competitors using AI in the legal space?",

    # Real Estate Sector (10)
    "How can AI find more sellers for my real estate agency?",
    "What is predictive seller identification?",
    "Can you automate my lead follow-up sequence?",
    "How do you consolidate leads from Zillow and Realtor.com?",
    "What is autonomous lead nurturing in real estate?",
    "How does AI help with distressed property tracking?",
    "Can you build a high-converting landing page for luxury listings?",
    "How do you handle CRM automation for agents?",
    "What is the value of automated property valuation for my clients?",
    "How can AI help me scale without hiring more assistants?",

    # General Consulting & Brand (5)
    "What is the Zymnix Path?",
    "Why do you focus on ROI instead of just building websites?",
    "How is Zymnix different from a traditional marketing agency?",
    "What is your philosophy on the balance between AI and human design?",
    "How do you ensure your AI solutions don't sound robotic?",

    # Edge cases & Missing Data (5)
    "Can you help me bake a sourdough bread?", # Testing scope/guards
    "Who is the current CEO of Microsoft?", # Testing general vs specific knowledge
    "Why should I choose you over a cheap freelancer?", # Testing value philosophy
    "Asdfghjkl;", # Testing gibberish handling
    "Do you have any case studies on AI for space exploration?" # Testing missing domain data
]

results = []

print(f"Begiining Stress Test: 50 Prompts against {API_URL}")
print("-" * 50)

for i, prompt in enumerate(prompts, 1):
    print(f"[{i}/50] Testing: {prompt[:50]}...")
    try:
        start_time = time.time()
        response = requests.post(API_URL, json={"message": prompt})
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            results.append({
                "id": i,
                "prompt": prompt,
                "response": data["response"],
                "tokens": data.get("tokens_used", {}),
                "duration": round(duration, 2),
                "status": "SUCCESS"
            })
            # Check for markdown bolding (the user hates this)
            if "**" in data["response"]:
                print(f"  ⚠️ ALERT: Markdown bolding detected in response {i}")
        else:
            print(f"  ❌ FAILED logic: {response.status_code}")
            results.append({"id": i, "prompt": prompt, "status": "API_ERROR", "code": response.status_code})
            
    except Exception as e:
        print(f"  ❌ FAILED connection: {str(e)}")
        results.append({"id": i, "prompt": prompt, "status": "CONNECTION_ERROR", "error": str(e)})

    # Small delay to avoid rate limiting
    time.sleep(1)

with open("stress_test_results.json", "w") as f:
    json.dump(results, f, indent=2)

print("-" * 50)
print(f"Test Complete. Results saved to stress_test_results.json")
