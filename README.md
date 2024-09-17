1. **Create a virtual environment**: 
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment**: 
   - On Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. **Install all dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Move to the next directory**:
   ```bash
   cd spiderweb
   ```

5. **Run the code**:
   ```bash
   scrapy crawl webcrawling
   ```