#!/usr/bin/env python3

import json
import sys

def load_resume_data(json_file):
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {json_file} not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        sys.exit(1)

def format_links(links):
    github_url = f"https://github.com/{links['github']}"
    linkedin_url = f"https://www.linkedin.com/in/{links['linkedin']}"
    github_link = f"[github.com/{links['github']}]({github_url})"
    linkedin_link = f"[linkedin.com/in/{links['linkedin']}]({linkedin_url})"
    website_link = f"[mhmdhoseinzade.ir]({links['website']})"
    return f"{github_link} | {linkedin_link} | {website_link}"

def format_contact(contact):
    email_link = f"[{contact['email']}](mailto:{contact['email']})"
    return f"{email_link} | {contact['phone']} | {contact['location']}"

def format_education(education):
    if not education:
        return ""
    
    result = "Education\n---------\n\n"
    for edu in education:
        result += f"{edu['period']} | {edu['degree']} | {edu['institution']}\n"
    
    result += "\n"
    return result

def format_experience(experience):
    if not experience:
        return ""
    
    result = "Experience\n----------\n\n"
    
    for exp in experience:
        result += f"### {exp['company']} | {exp['period']}\n"
        result += f"#### {exp['position']}\n\n"
        
        for achievement in exp['achievements']:
            if isinstance(achievement, dict):
                result += f"* {achievement['text']}\n"
            else:
                result += f"* {achievement}\n"
        
        result += "\n"
    
    return result

def format_skills(skills):
    if not skills:
        return ""
    
    result = "Skills\n---------\n"
    
    if 'languages' in skills and skills['languages']:
        result += f"Languages: {'  '.join(skills['languages'])}\n\n"
    
    if 'frameworks' in skills and skills['frameworks']:
        result += f"Frameworks: {'  '.join(skills['frameworks'])}\n\n"
    
    if 'devops' in skills and skills['devops']:
        result += f"DevOps: {', '.join(skills['devops'])}\n\n"
    
    if 'databases' in skills and skills['databases']:
        result += f"Databases: {', '.join(skills['databases'])}\n\n"
    
    if 'soft' in skills and skills['soft']:
        result += f"Soft:  {', '.join(skills['soft'])}\n\n"

    if 'concepts' in skills and skills['concepts']:
        result += f"Concepts: {', '.join(skills['concepts'])}\n\n"
    
    return result

def format_links_fa(links):
    github_url = f"https://github.com/{links['github']}"
    linkedin_url = f"https://www.linkedin.com/in/{links['linkedin']}"
    github_link = f"[github.com/{links['github']}]({github_url})"
    linkedin_link = f"[linkedin.com/in/{links['linkedin']}]({linkedin_url})"
    website_link = f"[mhmdhoseinzade.ir]({links['website']})"
    return f"{github_link} | {linkedin_link} | {website_link}"

def format_contact_fa(contact):
    email_link = f"[{contact['email']}](mailto:{contact['email']})"
    return f"{email_link} | {contact['phone']} | {contact['location']}"

def format_education_fa(education):
    if not education:
        return ""
    
    result = "تحصیلات\n---------\n\n"
    for edu in education:
        result += f"{edu['period']} | {edu['degree']} | {edu['institution']}\n"
    
    result += "\n"
    return result

def format_experience_fa(experience):
    if not experience:
        return ""
    
    result = "تجربه کاری\n----------\n\n"
    
    for exp in experience:
        result += f"### {exp['company']} | {exp['period']}\n"
        result += f"#### {exp['position']}\n\n"
        
        for achievement in exp['achievements']:
            if isinstance(achievement, dict):
                result += f"* {achievement['text']}\n"
            else:
                result += f"* {achievement}\n"
        
        result += "\n"
    
    return result

def format_skills_fa(skills):
    if not skills:
        return ""
    
    result = "مهارت‌ها\n---------\n"
    
    if 'languages' in skills and skills['languages']:
        result += f"زبان‌ها: {'  '.join(skills['languages'])}\n\n"
    
    if 'frameworks' in skills and skills['frameworks']:
        result += f"فریمورک‌ها: {'  '.join(skills['frameworks'])}\n\n"
    
    if 'devops' in skills and skills['devops']:
        result += f"DevOps: {', '.join(skills['devops'])}\n\n"
    
    if 'databases' in skills and skills['databases']:
        result += f"پایگاه‌داده‌ها: {', '.join(skills['databases'])}\n\n"
    
    if 'soft' in skills and skills['soft']:
        result += f"مهارت‌های نرم: {', '.join(skills['soft'])}\n\n"

    if 'concepts' in skills and skills['concepts']:
        result += f"مفاهیم: {', '.join(skills['concepts'])}\n\n"
    
    return result

def generate_readme(resume_data):
    readme = "<a id=\"en\"></a>\n\n"
    readme += f"# {resume_data['name']}\n"
    readme += f"{resume_data['title']}\n\n"
    
    readme += f"{format_links(resume_data['links'])}\n\n"
    
    readme += f"{format_contact(resume_data['contact'])}\n\n"
    
    readme += "Summary\n---------\n"
    readme += f"{resume_data['summary']}\n\n"
    
    readme += format_education(resume_data['education'])
    
    readme += format_experience(resume_data['experience'])
    
    readme += format_skills(resume_data['skills'])
    
    return readme

def generate_readme_fa(resume_data):
    readme = "<a id=\"fa\"></a>\n\n"
    readme += f"# {resume_data['name']}\n"
    readme += f"{resume_data['title']}\n\n"
    
    readme += f"{format_links_fa(resume_data['links'])}\n\n"
    
    readme += f"{format_contact_fa(resume_data['contact'])}\n\n"
    
    readme += "خلاصه\n---------\n"
    readme += f"{resume_data['summary']}\n\n"
    
    readme += format_education_fa(resume_data['education'])
    
    readme += format_experience_fa(resume_data['experience'])
    
    readme += format_skills_fa(resume_data['skills'])
    
    return readme

def main():
    json_file = "resume.json"
    json_file_fa = "resume.fa.json"
    output_file = "README.md"
    
    resume_data = load_resume_data(json_file)

    readme_content = (
        "Language / زبان\n"
        "--------------\n\n"
        "- [English](#en)\n"
        "- [فارسی](#fa)\n\n"
        "---\n\n"
    )
    readme_content += generate_readme(resume_data)

    try:
        resume_data_fa = load_resume_data(json_file_fa)
        readme_content += "\n---\n\n"
        readme_content += generate_readme_fa(resume_data_fa)
    except SystemExit:
        # Keep English README if Persian resume is missing
        pass
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print(f"Successfully converted {json_file} to {output_file}")
    except Exception as e:
        print(f"Error writing to {output_file}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
