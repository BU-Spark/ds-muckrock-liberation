# Project Research

## Sources by Teammates

### Quoc Dat Nguyen
- GAO (2017). *Military Personnel: DOD and the Coast Guard Need to Screen for Gambling Disorder Addiction and Update Guidance.* Government Accountability Office. [Link](https://www.gao.gov/assets/gao-17-114.pdf)  
- American Psychiatric Association (2013). *Diagnostic and Statistical Manual of Mental Disorders (5th ed.).* Washington, DC: American Psychiatric Publishing. [Link](https://psychiatryonline.org/doi/epub/10.1176/appi.books.9780890425596)  
- Harris, S. (2021). *Technology May Make Life Tougher for Service Members Struggling with Problematic Patterns of Gambling.* Health.mil. [Link](https://health.mil/Military-Health-Topics/Centers-of-Excellence/Psychological-Health-Center-of-Excellence/Clinicians-Corner-Blog/Special-Populations-and-Topics/Technology-May-Make-Life-Tougher-for-Service-Members-Struggling-with-Problematic-Patterns-of-Gambling?)  
- Young, M., Stevens, M., & Morris, M. (2012). *Electronic Gaming Machine Accessibility and Gambling Problems: A Natural Policy Experiment.* International Gambling Studies. [Link](https://pmc.ncbi.nlm.nih.gov/articles/PMC10562817/)  

### Ching Hsuan Lin
- Van der Maas, M., & Nower, L. (2021). *Gambling and Military Service: Characteristics, Comorbidity, and Problem Severity in an Epidemiological Sample.* Addictive Behaviors, 114, 106725. [Link](https://doi.org/10.1016/j.addbeh.2020.106725)  
- Etuk, R., Shirk, S. D., Grubbs, J., & Kraus, S. W. (2020). *Gambling Problems in US Military Veterans.* Current Addiction Reports, 7, 210–228. [Link](https://www.greo.ca/Modules/EvidenceCentre/files/Etuk%20et%20al%20%282020%29_Gambling%20problems%20in%20US%20military%20veterans_final.pdf?utm_source=chatgpt.com)  
- U.S. Government Accountability Office. (2025). *Military Personnel: More Guidance Could Help Address Service Member Gambling Problems (GAO-25-107700).* Washington, DC: U.S. Government Accountability Office. [Link](https://www.gao.gov/products/gao-25-107700)  

### Jyun-Ru Huang
- National Council on Problem Gambling. (2022). *Fact Sheet: Gambling & Addiction Among Servicemembers and Veterans.* [Link](https://www.ncpgambling.org/wp-content/uploads/2023/12/Fact-Sheet-Gambling-Addiction-Among-Servicemembers.pdf)  

### Pin-Hao Pan
- Lisenby, A., & Edgell, H. (2019). *Defense Dept. Cashes In On Overseas Slot Machines While Problem Gambling Is Largely Undiagnosed.* St. Louis Public Radio, February 4, 2019. [Link](https://news.stlpublicradio.org/government-politics-issues/2019-02-04/defense-dept-cashes-in-on-overseas-slot-machines-while-problem-gambling-is-largely-undiagnosed)  
- *The Big Money and High Cost of the US Military’s On-Base Slot Machines.* WIRED Magazine, August 2025. [Link](https://www.wired.com/story/us-military-on-base-slot-machines-gambling-addiction/)  

### Nithya Priya Jayakumar
- CNBC. (2024, July 3). *Concerns Grow Over Gambling Addiction in the Military.* [Link](https://www.cnbc.com/2024/07/03/concerns-grow-over-gambling-addiction-in-the-military-.html)  
- Paterson, M., Whitty, M., & Leslie, P. (2020). *Exploring the Prevalence of Gambling Harm Among Active Duty Military Personnel: A Systematic Scoping Review.* Journal of Gambling Studies, 37, 529–549. [Link](https://doi.org/10.1007/s10899-020-09951-4)  
- Yeager, D. (n.d.). *The Impact Problem Gambling Has on the Military, Veterans, Their Families, and Career.* Pennsylvania Council on Problem Gambling. Accessed September 29, 2025. [Link](https://www.pacouncil.com/wp-content/uploads/2023-PA-Conference.pdf)  

### Cameron Moore
- Yeager, D., & Taylor, R. (2025, July 31). *The Military Faces a Gambling Addiction Crisis. We’ve Lived It—On Both Sides.* National Council on Problem Gambling. [Link](https://www.ncpgambling.org/news/the-military-faces-a-gambling-addiction-crisis-weve-lived-it-on-both-sides/)  
- Emond, A., Griffiths, M. D., & Hollén, L. (2020). *Problem Gambling in Early Adulthood: A Population-Based Study.* International Journal of Mental Health and Addiction. [Link](https://pmc.ncbi.nlm.nih.gov/articles/PMC8930883/)  
- Kumar, A. (2025, July 21). *I Tested 7 Python PDF Extractors So You Don’t Have To (2025 Edition).* Medium. [Link](https://onlyoneaman.medium.com/i-tested-7-python-pdf-extractors-so-you-dont-have-to-2025-edition-c88013922257)  

## Proposed Methods
Because extracting financial statement information and charts from PDF files is central to this project—and financial reports often have hierarchical structures with tables that mix numbers and text—we evaluated the major Python packages for this task using the following criteria:

- **Table detection**: Accurately identify borders, headers, and cell contents.  
- **OCR support**: Provide OCR (Optical Character Recognition) capability, since some charts may come from scanned documents.  
- **Numerical accuracy**: Minimize errors in recognizing numerical data.  

### Tool Comparison

We reviewed several Python libraries for extracting financial data from PDFs and compared them on three criteria: table detection, OCR support, and numerical accuracy.

- **pdfplumber**: Provides excellent table detection, accurately identifying cells and contents using multiple border-detection strategies. Although it lacks built-in OCR, it achieves high numerical accuracy, handling layouts cleanly even in complex tables.

- **tabula-py**: Uses a Java-based detection method that works well for multi-page tables but struggles with irregular or complex layouts. It does not have built-in OCR, and while it is accurate on simple tables, formatting issues often appear in more complex ones. Its numerical accuracy is considered medium.

- **Camelot**: Uses advanced computer vision for precise border and layout detection. It is limited to text-based PDFs (no OCR support), but when applicable, it delivers excellent table detection and high numerical accuracy.

- **pypdf**: Offers only basic text extraction and does not include table detection or OCR capabilities. Because of this, its numerical accuracy is low, as general text parsing often introduces errors.

- **PyMuPDF (fitz)**: Includes a fair-quality built-in table extractor and supports OCR via Tesseract. While not as strong in table detection, it can be useful for scanned documents. Its numerical accuracy is medium, suitable for custom extraction tasks, though it often requires tailored code for reliability.

There is no single PDF-handling tool that can fully accomplish our task. Each type of chart requires a different tool for extraction, and we will need to manually determine which one performs best depending on the structure of the document.
