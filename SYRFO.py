import os
import sys
import argparse
import concurrent.futures
import requests

# إلغاء تحذيرات الاتصال غير الآمن
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# ألوان ANSI للتنسيق البصري في التيرمينال
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

def banner():
    print(f"""{CYAN}
   ███████╗██╗   ██╗██████╗ ███████╗ ██████╗ 
   ██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔═══██╗
   ███████╗ ╚████╔╝ ██████╔╝█████╗  ██║   ██║
   ╚════██║  ╚██╔╝  ██╔══██╗██╔══╝  ██║   ██║
   ███████║   ██║   ██║  ██║██║     ╚██████╔╝
   ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝      ╚═════╝ 
        [ Advanced Subdomain Fuzzing Tool ]
{RESET}""")

def check_subdomain(sub, domain, timeout):
    url = f"https://{sub}.{domain}"
    try:
        response = requests.get(url, timeout=timeout, allow_redirects=True, verify=False)
        return {"url": url, "status": response.status_code, "success": True}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "ConnectionError"}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Timeout"}
    except Exception:
        return {"success": False, "error": "Other"}

def main():
    banner()
    
    parser = argparse.ArgumentParser(description="أداة SYRFO الاحترافية المتقدمة لفحص النطاقات الفرعية")
    parser.add_argument("-u", "--domain", required=True, help="الموقع المراد فحصه (مثال: syriatalk.org)")
    # تم تعديل القيمة الافتراضية لتصبح محلية ضمن مجلد الأداة مباشرة
    parser.add_argument("-w", "--wordlist", default="subdomains.txt", help="مسار ملف القائمة (افتراضي: subdomains.txt)")
    parser.add_argument("-t", "--threads", type=int, default=20, help="عدد الخيوط للسرعة الفائقة (افتراضي: 20)")
    parser.add_argument("-o", "--output", default="syrfo_results.txt", help="ملف حفظ النتائج النشطة (افتراضي: syrfo_results.txt)")
    parser.add_argument("--timeout", type=int, default=3, help="مهلة الاتصال بالثواني (افتراضي: 3)")
    
    args = parser.parse_args()

    domain = args.domain
    wordlist_path = args.wordlist
    threads_count = args.threads
    output_file = args.output
    timeout = args.timeout

    if not os.path.exists(wordlist_path):
        print(f"{RED}[!] خطأ: ملف القائمة غير موجود في المسار الحالي: {wordlist_path}{RESET}")
        print(f"{YELLOW}[*] تأكد من وجود ملف subdomains.txt في نفس مجلد الأداة.{RESET}")
        sys.exit(1)

    with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as f:
        subdomains = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    total_subs = len(subdomains)
    print(f"{YELLOW}[*] Target Domain : {CYAN}{domain}{RESET}")
    print(f"{YELLOW}[*] Wordlist Path : {CYAN}{wordlist_path}{RESET}")
    print(f"{YELLOW}[*] Total Loaded  : {CYAN}{total_subs} subdomains{RESET}")
    print(f"{YELLOW}[*] Threads Count : {CYAN}{threads_count}{RESET}")
    print(f"{CYAN}--------------------------------------------------{RESET}")
    print(f"{YELLOW}[*] Starting fast enumeration... (Press Ctrl+C to stop){RESET}\n")

    active_results = []
    failed_count = 0
    completed_count = 0

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads_count) as executor:
            future_to_sub = {executor.submit(check_subdomain, sub, domain, timeout): sub for sub in subdomains}
            
            for future in concurrent.futures.as_completed(future_to_sub):
                completed_count += 1
                result = future.result()
                
                sys.stdout.write(f"\r{YELLOW}[Progress: {completed_count}/{total_subs}] Active Found: {len(active_results)}{RESET}")
                sys.stdout.flush()

                if result["success"]:
                    active_results.append(result)
                    print(f"\r\033[K{GREEN}[+] Active: {result['url']} | Status: {result['status']}{RESET}")
                else:
                    failed_count += 1

    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}[!] تم إيقاف الفحص يدوياً بواسطة المستخدم (Ctrl + C).{RESET}")

    if active_results:
        with open(output_file, "w", encoding="utf-8") as out:
            for res in active_results:
                out.write(f"{res['url']} (Status: {res['status']})\n")

    print("\n" + "=" * 54)
    print(f"{CYAN}               [ تقرير النتائج النهائية ]              {RESET}")
    print("=" * 54)
    print(f"[*] إجمالي المحاولات المفحوصة : {completed_count} من {total_subs}")
    print(f"[*] النطاقات النشطة المكتشفة : {GREEN}{len(active_results)}{RESET}")
    print(f"[*] النطاقات غير المتاحة    : {failed_count}")
    print("-" * 54)

    if active_results:
        print(f"{GREEN}[+] قائمة الروابط النشطة:{RESET}")
        for res in active_results:
            print(f"    {GREEN}• {res['url']}  (Status: {res['status']}){RESET}")
        print(f"\n{CYAN}[*] تم حفظ النتائج بنجاح في الملف: {output_file}{RESET}")
    else:
        print(f"{RED}[-] لم يتم العثور على أي نطاقات فرعية نشطة.{RESET}")

    print("=" * 54)

if __name__ == "__main__":
    main()
