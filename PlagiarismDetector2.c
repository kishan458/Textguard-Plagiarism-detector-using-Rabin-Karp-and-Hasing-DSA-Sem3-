#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <math.h>
#include <stdbool.h>

/**
 * TEXTGUARD ADVANCED ENGINE (C VERSION - RANKING ENABLED)
 * Includes: Bloom Filter, Winnowing, and Frequency Ranking via Heap Logic.
 */

#define MAX_TEXT 100000
#define MAX_WORDS 20000
#define MAX_WORD_LEN 64
#define BLOOM_SIZE 1000000
#define MOD1 1000000007LL
#define MOD2 1000000009LL
#define BASE 131LL
#define TABLE_SIZE 100003
#define TOP_K 5

// --- DATA STRUCTURES ---

//double hash of an n-gram.
typedef struct {
    long long h1;
    long long h2;
} Fingerprint;


typedef struct {
    unsigned char *bits;
    int size;
} BloomFilter;

typedef struct {
    Fingerprint *items;
    bool *occupied;
    int capacity;
    int size;
} FingerprintSet;

// Structure to track how many times a matching phrase appeared
typedef struct {
    Fingerprint fp;
    char phrase[MAX_WORD_LEN * 5]; // Store actual text for display
    int frequency;
    bool occupied;
} FreqEntry;

//ranking plagiarism intensity
typedef struct {
    FreqEntry *table;
    int capacity;
} FrequencyMap;

// --- UTILITIES ---

// Function to read entire file content into a string
char* read_file(const char* filename) {
    FILE *f = fopen(filename, "rb");
    if (!f) return NULL;
    fseek(f, 0, SEEK_END);
    long length = ftell(f);
    fseek(f, 0, SEEK_SET);
    char *buffer = malloc(length + 1);
    if (buffer) {
        fread(buffer, 1, length, f);
        buffer[length] = '\0';
    }
    fclose(f);
    return buffer;
}

char* preprocess(const char *text) {
    char *clean = malloc(strlen(text) + 1);
    int j = 0;
    for (int i = 0; text[i]; i++) {
        if (isalnum(text[i])) clean[j++] = (char)tolower(text[i]);
        else if (j > 0 && clean[j-1] != ' ') clean[j++] = ' ';
    }
    clean[j] = '\0';
    return clean;
}

int tokenize(char *clean, char words[MAX_WORDS][MAX_WORD_LEN]) {
    int count = 0;
    char *token = strtok(clean, " ");
    while (token && count < MAX_WORDS) {
        strncpy(words[count++], token, MAX_WORD_LEN - 1);
        token = strtok(NULL, " ");
    }
    return count;
}

// --- BLOOM FILTER ---

BloomFilter* create_bloom() {
    BloomFilter *bf = malloc(sizeof(BloomFilter));
    bf->size = BLOOM_SIZE;
    bf->bits = calloc((BLOOM_SIZE / 8) + 1, sizeof(unsigned char));
    return bf;
}

void bloom_add(BloomFilter *bf, Fingerprint f) {
    int idx1 = abs((int)(f.h1 % bf->size));
    int idx2 = abs((int)(f.h2 % bf->size));
    bf->bits[idx1/8] |= (1 << (idx1%8));
    bf->bits[idx2/8] |= (1 << (idx2%8));
}

bool bloom_check(BloomFilter *bf, Fingerprint f) {
    int idx1 = abs((int)(f.h1 % bf->size));
    int idx2 = abs((int)(f.h2 % bf->size));
    if (!(bf->bits[idx1/8] & (1 << (idx1%8)))) return false;
    if (!(bf->bits[idx2/8] & (1 << (idx2%8)))) return false;
    return true;
}

// --- HASH SETS & FREQUENCY MAP ---

FingerprintSet* create_set() {
    FingerprintSet *fs = malloc(sizeof(FingerprintSet));
    fs->capacity = TABLE_SIZE;
    fs->items = malloc(sizeof(Fingerprint) * TABLE_SIZE);
    fs->occupied = calloc(TABLE_SIZE, sizeof(bool));
    fs->size = 0;
    return fs;
}

void set_insert(FingerprintSet *fs, Fingerprint f) {
    int idx = abs((int)(f.h1 % fs->capacity));
    while (fs->occupied[idx]) {
        if (fs->items[idx].h1 == f.h1 && fs->items[idx].h2 == f.h2) return;
        idx = (idx + 1) % fs->capacity;
    }
    fs->items[idx] = f;
    fs->occupied[idx] = true;
    fs->size++;
}

bool set_contains(FingerprintSet *fs, Fingerprint f) {
    int idx = abs((int)(f.h1 % fs->capacity));
    while (fs->occupied[idx]) {
        if (fs->items[idx].h1 == f.h1 && fs->items[idx].h2 == f.h2) return true;
        idx = (idx + 1) % fs->capacity;
    }
    return false;
}

FrequencyMap* create_freq_map() {
    FrequencyMap *fm = malloc(sizeof(FrequencyMap));
    fm->capacity = TABLE_SIZE;
    fm->table = calloc(TABLE_SIZE, sizeof(FreqEntry));
    return fm;
}

void freq_update(FrequencyMap *fm, Fingerprint f, char *phrase) {
    int idx = abs((int)(f.h1 % fm->capacity));
    while (fm->table[idx].occupied) {
        if (fm->table[idx].fp.h1 == f.h1 && fm->table[idx].fp.h2 == f.h2) {
            fm->table[idx].frequency++;
            return;
        }
        idx = (idx + 1) % fm->capacity;
    }
    fm->table[idx].fp = f;
    fm->table[idx].frequency = 1;
    strncpy(fm->table[idx].phrase, phrase, sizeof(fm->table[idx].phrase) - 1);
    fm->table[idx].occupied = true;
}

// --- HEAP RANKING LOGIC ---

void swap(FreqEntry *a, FreqEntry *b) {
    FreqEntry temp = *a;
    *a = *b;
    *b = temp;
}

void min_heapify(FreqEntry heap[], int n, int i) {
    int smallest = i;
    int l = 2 * i + 1;
    int r = 2 * i + 2;
    if (l < n && heap[l].frequency < heap[smallest].frequency) smallest = l;
    if (r < n && heap[r].frequency < heap[smallest].frequency) smallest = r;
    if (smallest != i) {
        swap(&heap[i], &heap[smallest]);
        min_heapify(heap, n, smallest);
    }
}

// --- CORE LOGIC ---

Fingerprint get_double_hash(char words[][MAX_WORD_LEN], int start, int n) {
    long long h1 = 0, h2 = 0;
    for (int i = 0; i < n; i++) {
        for (int j = 0; words[start + i][j]; j++) {
            h1 = (h1 * BASE + words[start + i][j]) % MOD1;
            h2 = (h2 * BASE + words[start + i][j]) % MOD2;
        }
        if (i < n - 1) { h1 = (h1 * BASE + ' ') % MOD1; h2 = (h2 * BASE + ' ') % MOD2; }
    }
    return (Fingerprint){h1, h2};
}

int main() {
    char *docA = NULL, *docB = NULL;
    char buffer[MAX_TEXT];
    int choice;

    printf("=== TEXTGUARD C-CORE (FREQUENCY RANKING MODE) ===\n");
    printf("Select Input Mode:\n");
    printf("1. Manual Text Entry\n");
    printf("2. Read from .txt Files\n");
    printf("Choice: ");
    scanf("%d", &choice);
    getchar(); // clear newline

    if (choice == 1) {
        printf("\nEnter Original Document (A):\n");
        fgets(buffer, MAX_TEXT, stdin);
        docA = strdup(buffer);
        printf("\nEnter Suspect Document (B):\n");
        fgets(buffer, MAX_TEXT, stdin);
        docB = strdup(buffer);
    } else {
        char filename[256];
        printf("\nEnter filename for Original (A) (e.g., doc1.txt): ");
        scanf("%s", filename);
        docA = read_file(filename);
        printf("Enter filename for Suspect (B) (e.g., doc2.txt): ");
        scanf("%s", filename);
        docB = read_file(filename);
        
        if (!docA || !docB) {
            printf("Error: Could not read files. Ensure they exist in the directory.\n");
            return 1;
        }
    }

    int n = 3, w = 3;
    printf("\n--- Analysis Start ---\n");

    // 1. Prepare Doc A
    char *cleanA = preprocess(docA);
    char wordsA[MAX_WORDS][MAX_WORD_LEN];
    int wcA = tokenize(cleanA, wordsA);
    int numHashesA = wcA - n + 1;
    Fingerprint *hashesA = malloc(sizeof(Fingerprint) * numHashesA);
    for (int i = 0; i < numHashesA; i++) hashesA[i] = get_double_hash(wordsA, i, n);

    FingerprintSet *fpsA = create_set();
    BloomFilter *bf = create_bloom();
    for (int i = 0; i <= numHashesA - w; i++) {
        Fingerprint minF = hashesA[i];
        for (int j = 1; j < w; j++) if (hashesA[i+j].h1 < minF.h1) minF = hashesA[i+j];
        set_insert(fpsA, minF);
        bloom_add(bf, minF);
    }

    // 2. Scan Doc B and Track Frequencies
    char *cleanB = preprocess(docB);
    char wordsB[MAX_WORDS][MAX_WORD_LEN];
    int wcB = tokenize(cleanB, wordsB);
    int numHashesB = wcB - n + 1;
    int total_matches = 0;
    FrequencyMap *fm = create_freq_map();

    for (int i = 0; i < numHashesB; i++) {
        Fingerprint f = get_double_hash(wordsB, i, n);
        if (bloom_check(bf, f) && set_contains(fpsA, f)) {
            total_matches++;
            // Reconstruct phrase for the frequency map
            char phrase[256] = "";
            for(int k=0; k<n; k++) { strcat(phrase, wordsB[i+k]); if(k<n-1) strcat(phrase, " "); }
            freq_update(fm, f, phrase);
        }
    }

    // 3. Extract Top K using Min-Heap
    FreqEntry heap[TOP_K];
    int heapSize = 0;
    for (int i = 0; i < TABLE_SIZE; i++) {
        if (fm->table[i].occupied) {
            if (heapSize < TOP_K) {
                heap[heapSize] = fm->table[i];
                heapSize++;
                if (heapSize == TOP_K) {
                    for (int j = (TOP_K / 2) - 1; j >= 0; j--) min_heapify(heap, TOP_K, j);
                }
            } else if (fm->table[i].frequency > heap[0].frequency) {
                heap[0] = fm->table[i];
                min_heapify(heap, TOP_K, 0);
            }
        }
    }

    // 4. Final Display
    double score = (double)total_matches / (fpsA->size) * 100.0;
    printf("\nOverall Verbatim Score: %.1f%%\n", score);
    printf("\nTOP %d MOST FREQUENT PLAGIARIZED PHRASES:\n", heapSize);
    printf("--------------------------------------------------\n");
    for (int i = heapSize - 1; i >= 0; i--) {
        printf("[%d] Freq: %d | Phrase: \"%s\"\n", heapSize - i, heap[i].frequency, heap[i].phrase);
    }

    // Cleanup
    free(docA); free(docB); free(cleanA); free(cleanB); free(hashesA);
    return 0;
}