<div align="center">
  <h1> TextGuard Ultra v5.0</h1>
  <p><b>Advanced Plagiarism Detection & Forensic Intelligence Engine</b></p>
  <p><i>Leveraging Rabin-Karp, Winnowing, and Min-Heap architectures for high-speed document analysis.</i></p>
</div>

<hr />

<h2> Overview</h2>
<p>
  <b>TextGuard Ultra</b> is a high-performance plagiarism detection platform designed to identify both verbatim copying and intelligent paraphrasing. Unlike basic string-matching tools, TextGuard uses <b>document fingerprinting (Winnowing)</b> and <b>Bloom Filter gatekeeping</b> to scan large texts with O(N) efficiency. 
</p>



<hr />

<h2> Core DSA Engine</h2>
<p>The platform is built on four pillars of computer science to ensure speed and accuracy:</p>

<ul>
  <li><b>Rabin-Karp Rolling Hash:</b> Converts text "shingles" into numerical values for rapid comparison.</li>
  <li><b>Winnowing Algorithm:</b> Selects a subset of hashes (fingerprints) to represent a document, significantly reducing memory footprint while maintaining detection sensitivity.</li>
  <li><b>Bloom Filter:</b> Acts as a high-speed probabilistic gatekeeper to immediately skip non-matching segments, reducing the workload on the main engine.</li>
  <li><b>Min-Heap Ranking:</b> Utilizes a <code>heapq</code> structure to maintain the Top-K most frequent plagiarized phrases with <code>O(N log K)</code> complexity.</li>
</ul>

<hr />

<h2> Key Features</h2>
<ul>
  <li><b> Forensic Scan:</b> Identifies exact verbatim matches using n-gram fingerprinting.</li>
  <li><b> Semantic Overlap:</b> Uses <b>TF-IDF Vectorization</b> and <b>Cosine Similarity</b> to detect paraphrased content that traditional scanners miss.</li>
  <li><b> Stylometry Analysis:</b> Compares sentence length and vocabulary richness to identify "ghostwriting" signatures.</li>
  <li><b> Cyber-Forensic UI:</b> A premium, glassmorphism-inspired Streamlit interface for a modern user experience.</li>
</ul>

<hr />

<h2> Tech Stack</h2>
<table width="100%">
  <tr>
    <th>Layer</th>
    <th>Technologies</th>
  </tr>
  <tr>
    <td><b>UI Framework</b></td>
    <td>Streamlit (Custom CSS Glassmorphism)</td>
  </tr>
  <tr>
    <td><b>DSA Logic</b></td>
    <td>Python, NumPy, Heapq (Min-Heap)</td>
  </tr>
  <tr>
    <td><b>NLP & ML</b></td>
    <td>Scikit-learn (TF-IDF, Cosine Similarity)</td>
  </tr>
  <tr>
    <td><b>Text Processing</b></td>
    <td>Regex, N-gram Tokenization</td>
  </tr>
</table>

<hr />

<h2> Performance Report & Results</h2>
<p>TextGuard categorizes findings into three intelligence levels:</p>

<table>
  <tr>
    <th>Verdict</th>
    <th>Trigger Condition</th>
    <th>Analysis</th>
  </tr>
  <tr>
    <td><b> CRITICAL</b></td>
    <td>Verbatim > 25%</td>
    <td>Massive structural similarity; evidence of copy-paste.</td>
  </tr>
  <tr>
    <td><b> WARNING</b></td>
    <td>Semantic > 60%</td>
    <td>Thematic overlap; likely "intelligent" paraphrasing.</td>
  </tr>
  <tr>
    <td><b> AUTHENTIC</b></td>
    <td>Low Scores</td>
    <td>High originality; low structural or thematic overlap.</td>
  </tr>
</table>



<hr />

<h2>⚙️ Local Setup Instructions</h2>

<h3>1. Clone the Repository</h3>
<pre><code>git clone https://github.com/yourusername/TextGuard-Ultra.git
cd TextGuard-Ultra</code></pre>

<h3>2. Install Dependencies</h3>
<pre><code>pip install streamlit numpy scikit-learn</code></pre>

<h3>3. Run the Platform</h3>
<pre><code>streamlit run main.py</code></pre>

<hr />

<div align="center">
  <p>Developed for Academic Integrity and Algorithmic Excellence</p>
</div>
