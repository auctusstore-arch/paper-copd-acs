# Plan: Revisi Manuskrip Two-Clock COPD-ACS

## Context

Manuskrip "Beyond Inflammatory Spillover: A Two-Clock Model of Cardiovascular Risk in COPD" (Hendri Susilo) saat ini berstatus **Major Revision di ambang reject**. Audit peer-review (`Checklist revisi/checklist_revisi_two_clock.html`) menemukan 33 butir revisi (8 kritis, 16 mayor, 9 minor) di 5 tahap bergerbang, termasuk dua defect level-integritas: klaim yang salah mengutip temuan sumbernya sendiri (C1), dan perbandingan satuan yang tidak valid (C2). C1 dan C2 adalah hard gate — rekomendasi tetap Major Revision sampai keduanya benar-benar diperbaiki.

Tujuan sesi ini: hasilkan draf revisi lengkap (docx baru, terpisah dari file asli yang read-only) yang menjawab seluruh 33 butir, memakai bahasa akademik sesuai gaya *CJC Open* (`Contoh review article/main.pdf`), bebas pola tulisan AI (stop-slop), dan diperluas dengan literatur dari `Rangkuman consensus/` + `Jurnal bacaan/` plus retrieval web untuk ~20 referensi yang dituntut checklist tapi belum ada di folder (IAMI, BICS, PACE, Higbee 2021, Au Yeung 2022, CANTOS/CIRT/COLCOT, DETO2X-AMI, Smeeth 2004, Kwong 2018, dll).

Konfirmasi user: retrieval literatur via web search/PubMed untuk verifikasi angka kunci; desain ulang central illustration cukup sebagai brief tertulis (bukan re-render gambar); eksekusi dengan checkpoint per tahap — berhenti untuk review user setelah Tahap 1 selesai, karena koreksi C1/C2 mengubah argumen inti (angka OR 1,004, framing abstrak dan judul).

## Prinsip kerja yang berlaku di semua tahap

1. **File asli read-only.** Semua kerja terjadi di `Manuskrip/COPD_ACS_Two_Clock_Model_Review_REVISED.docx` (copy dari original, dibuat di awal Tahap 1). File asli tidak pernah ditulis.
2. **Draft di teks dulu, sinkron ke docx per tahap.** Menulis ulang §1-13 langsung di docx untuk perubahan sebesar ini lambat dan sulit di-review. Pendekatan: draft tiap bagian sebagai teks biasa di scratchpad untuk direview cepat, lalu di akhir tiap Tahap, sinkronkan ke docx sekaligus (skill `anthropic-skills:docx`) dengan tracked changes terhadap draf sebelumnya.
3. **Tiga aturan penulisan berlaku dari awal, bukan hanya di Tahap 4** (supaya tidak menulis ulang dua kali): tidak ada em dash; ikuti stop-slop (`stop-slop-main/SKILL.md` + `references/phrases.md` + `references/structures.md`) untuk kalimat baru; register akademik sesuai exemplar CJC Open (hedged, sitasi > asersi, "we" bukan narator jarak-jauh). Tahap 4 tetap jadi pass konsolidasi akhir untuk keseluruhan naskah (pangkas ~20%, gabung §4-6).
4. **Setiap klaim yang terikat ke paper spesifik: baca papernya**, jangan andalkan ingatan/summary AI (`Rangkuman consensus/` hanya jadi peta jalan ke sumber primer, tidak pernah dikutip langsung).
5. **Verifikasi sitasi**: setiap referensi dicek PubMed/DOI sebelum masuk daftar pustaka final; tidak ada penanda `[to be verified]`/`[to be completed]` yang tersisa.
6. Perlu load tool `WebSearch`/`WebFetch` (deferred) via ToolSearch di awal eksekusi untuk retrieval literatur.

## Tahap 0 — Retrieval literatur (prasyarat lintas-tahap)

Sebelum menulis konten, kumpulkan sumber yang dituntut checklist tapi belum ada lokal. Pakai WebSearch/WebFetch untuk PubMed/DOI/abstrak; catat HR/OR/CI/p-value yang dibutuhkan setiap butir checklist. Prioritas (dipakai di Tahap 1-3):

- Yu et al. 2024 (PMC11439898) — full text, untuk C1 (re-baca Tabel 2 & 3)
- Higbee ERJ 2021;58:2003196 — untuk C3, M10
- Au Yeung Thorax 2022;77:164-171 — untuk C3, M9
- Wielscher Genome Med 2021;13:104; Zhu Respir Res 2019;20:64 — untuk C3
- Fröbert (IAMI) Circulation 2021;144:1476-1484 — untuk M2
- BICS JAMA 2024;332:462-470; PACE Lancet Respir Med 2025 — untuk C4
- CANTOS NEJM 2017; CIRT NEJM 2019; COLCOT; LoDoCo2 — untuk M3
- Muller 1989; Mittleman & Mostofsky Circulation 2011; Smeeth NEJM 2004;351:2611-18; Kwong NEJM 2018;378:345-53; Warren-Gash J Infect Dis 2012 — untuk M1
- DETO2X-AMI NEJM 2017; ESC ACS 2023; ACC/AHA 2025 — untuk M13, C7b
- Aleva et al. Chest 2017 (prevalensi PE pada AECOPD) — untuk M11
- High-STEACS (Chapman JAMA 2017) — untuk M12
- ABYSS NEJM 2024; REBOOT/BETAMI-DANBLOCK 2025 — untuk C4
- 3-5 review naratif 2020-2026 (untuk cek framing spillover) — untuk F1
- Sumber pengganti C7b: literatur troponin-AECOPD mainstream (ganti [22] Cureus), referensi EKG standar (ganti [23])

Simpan ringkasan temuan (angka + full citation terverifikasi) di scratchpad sebagai referensi kerja untuk semua tahap berikutnya.

## Tahap 1 — Integritas (C1, C2, C3, C7a, C7b) — GATE, checkpoint setelah ini

1. Copy manuskrip asli ke `Manuskrip/COPD_ACS_Two_Clock_Model_Review_REVISED.docx`.
2. **C1**: Baca ulang Yu et al. 2024 Tabel 2 & 3. Tulis ulang §1¶4 dan seluruh §5 sesuai data aktual — BMI/smoking initiation/smoking status TIDAK menghapus asosiasi COPD→CHD (mereka biarkan signifikan); yang mengatenuasi adalah IL-6, LDL, kolesterol total (pola mediasi inflamasi, bukan konfounding). FEV1 bukan bagian MVMR, ia mediator.
3. **C2**: Hapus semua klaim "clinically indistinguishable from nothing" yang bersandar pada OR 1,004 vs risiko observasional 2-5×. OR 1,004 adalah skala liability model (ukb-d-I9_CHD), bukan OR epidemiologis — jangan dibandingkan langsung. Desain ulang spesifikasi Panel C central illustration (bagian dari brief Tahap 4/P1, tapi keputusan skala harus dikunci di sini).
4. **C3**: Tambahkan triangulasi ≥3 studi MR berdampingan (Higbee, Au Yeung, Wielscher, Zhu) di §5, laporkan heterogenitas secara terbuka, termasuk temuan reverse-causation absurd dari ref [7] sebagai alasan tidak bertumpu pada satu studi.
5. **C7a**: Verifikasi seluruh 36 referensi terhadap PubMed/DOI (pakai hasil Tahap 0 + retrieval tambahan untuk sisa referensi lokal manuskrip yang belum dicek). Hilangkan semua 17 penanda `[to be verified]`/`[to be completed]`.
6. **C7b**: Ganti ref [22] (Cureus, klaim troponin), [23] (Eur J Cardiovasc Med, klaim EKG), [34] (Australian Resuscitation Council 2011, klaim oksigen → ganti DETO2X-AMI + ESC ACS 2023), [35] (tesis Lund, hapus atau ganti publikasi peer-review penulis yang sama).
7. Sinkronkan hasil ke docx dengan tracked changes.
8. **Checkpoint**: presentasikan ringkasan perubahan C1-C7b ke user untuk konfirmasi sebelum lanjut Tahap 2, karena ini mengubah angka dan framing yang dipakai di abstrak, judul, dan §1.

## Tahap 2 — Bukti yang hilang (M2, C4, M3, M1, M9, M10)

1. **M2**: Tambahkan IAMI (Fröbert 2021) sebagai natural experiment utama pengganti argumen β-blocker tunggal di §9 (bagian baru), plus IVVE dan meta-analisis vaksinasi influenza-CV terbaru.
2. **C4**: Tulis ulang §9.2 — masukkan BICS dan PACE, turunkan klaim BLOCK-COPD dari "natural experiment paling tajam" menjadi "hipotesis efek-modifikasi yang belum diuji secara acak", nyatakan confounding by indication + healthy-adherer bias, kualifikasi dengan ABYSS dan REBOOT/BETAMI-DANBLOCK. Update Tabel 4 (tambah baris BICS/PACE).
3. **M3**: Di §3 dan §11, sebutkan CANTOS/CIRT/COLCOT/LoDoCo2. Reformulasi pertanyaan dari "apakah inflamasi menyebabkan kejadian koroner" menjadi "apakah COPD menambah beban inflamasi di atas paparan bersama". Perbaiki Prediksi 5 di Tabel 5 (efek colchicine/anti-IL-6 tidak dimodifikasi status COPD setelah stratifikasi hsCRP).
4. **M1**: Di §1 dan §7, kutip Muller 1989, Mittleman & Mostofsky 2011, Smeeth 2004, Kwong 2018, Warren-Gash 2012. Reposisi novelty: COPD sebagai kasus khusus di mana kedua jam bisa diinterogasi dalam populasi sama dengan desain berbeda.
5. **M9**: Di §5, tampilkan Au Yeung 2022 berdampingan dengan Higbee, jelaskan trade-off collider bias (conditioning tinggi badan) vs confounding.
6. **M10**: Perbaiki "FEV1 = obstruction term" — ganti jadi "kapasitas (FVC) / rasio (FEV1/FVC)"; kutip hasil FEV1/FVC dari Higbee secara eksplisit.
7. Sinkronkan ke docx dengan tracked changes.

## Tahap 3 — Metodologi dan argumen (C5, C6, M6, M7, M8, M4, M5, F1, M11, M12, M13, M14)

1. **C5**: Tambahkan sub-seksi baru di §6 yang menghadapi tiga bias SCCS: detection bias, protopathic bias, time-varying confounding. Laporkan estimat risiko pada jendela pra-eksposur jika tersedia dari sumber Rothnie/Donaldson.
2. **C6**: Reformulasi Prediksi 2 (Tabel 5) ke skala absolut, bukan proporsional — data Rothnie sendiri menunjukkan IRR lebih tinggi pada eksaserbator jarang. Manfaatkan temuan Rothnie yang belum dipakai (NSTEMI > STEMI).
3. **M6** (nilai tertinggi): Hitung PAF fast clock di §7.1 (baru) memakai formula PAF = Σpₑ(IRRₑ−1) / [1+Σpₑ(IRRₑ−1)] dengan IRR berat ≈2,58/sedang ≈1,58, jendela ≈91 hari, laju eksaserbasi berat 0,15-0,3/tahun dan sedang 0,8-1,5/tahun. Hitung pakai `uv run python3`, laporkan rentang hasil dan nyatakan implikasinya (mayoritas beban tetap substrat-driven).
4. **M7**: Perbaiki inkonsistensi Tabel 1 vs Tabel 3 — jam memetakan ke mekanisme, bukan tipe MI. Perbaiki baris "Dominant event type" Tabel 1.
5. **M8**: Ubah Tabel 5 dari prediksi kualitatif ke kuantitatif a priori dengan besaran dan arah eksplisit (contoh ARR per 100 pasien-tahun untuk Prediksi 2).
6. **M4**: Perbaiki non sequitur STATCOPE di §4 — pisahkan arah argumen (paru→sirkulasi vs sirkulasi→paru); jika data biomarker ICS/SUMMIT tidak tersedia, akui keberatan farmakologis tetap terbuka.
7. **M5**: Kalibrasi ulang pembacaan null SUMMIT di §1, §4, §12 — hapus "did nothing detectable to the heart", akui CI bawah 0,75 = manfaat relatif 25%.
8. **F1**: Kutip 3-5 review naratif 2020-2026 (termasuk ref [32] Singh 2024, GOLD 2025, Leong & Bardin) untuk cek klaim "organises most narrative reviews"; turunkan framing jika perlu jadi "penekanan yang salah tempat".
9. **M11**: Tambahkan paragraf komposisi outcome pasca-eksaserbasi (gagal jantung, aritmia lebih dominan dari MI) di §6/§8, dan beri PE (prevalensi ≈16% AECOPD, Aleva Chest 2017) perlakuan layak sebagai kompetitor narasi.
10. **M12**: Kutip proporsi CAD pada type 2 MI secara eksplisit di §8; verifikasi klaim "roughly half" terhadap High-STEACS.
11. **M13**: Ganti [34] dengan DETO2X-AMI + ESC ACS 2023 di §10; reformulasi konvergensi ke oksigen konservatif.
12. **M14**: Susun Supplementary Methods terpisah (string pencarian lengkap, tanggal, database, pernyataan kepatuhan SANRA) — deliverable file baru, bukan bagian §2 utama, tapi §2 dirujuk ke situ.
13. Sinkronkan ke docx dengan tracked changes.

## Tahap 4 — Presentasi (P1-P7)

1. **P1**: Tulis brief redesain central illustration (bukan gambar baru) — kurangi densitas teks drastis per panel, desain ulang Panel C sesuai keputusan C2 (jangan plot OR MR skala-liabilitas pada sumbu sama dengan HR/IRR observasional), label eksplisit "conceptual schematic" pada gambar. Simpan sebagai dokumen brief terpisah untuk user/desainer.
2. **P2**: Gabungkan atau bedakan tegas fungsi Tabel 1 vs Tabel 2 (Tabel 1 = anatomi model, Tabel 2 = bukti per desain).
3. **P3**: Pass konsolidasi seluruh naskah — pangkas ~20% prosa, hilangkan retorika berulang ("Honesty requires...", "the point with clinical teeth", dll — sisakan maks 3-4), gabungkan §4-6 yang mengulang materi sama.
4. **P4**: Tambahkan front/back matter: conflict of interest, funding, data availability, author contribution, ethics statement, pernyataan penggunaan AI dalam penyusunan.
5. **P5**: Pertimbangkan ulang judul — opsi "substrate-trigger model" atau pertahankan "slow clock" + ganti "fast clock" jadi "trigger switch". Sesuaikan agar tidak overclaim cakupan COPD terhadap slow clock.
6. **P6**: Turunkan overclaim abstrak ("little or no independent causal effect" tidak bertahan pasca C1-C3), tambahkan satu kalimat kuantifikasi PAF dari M6.
7. **P7**: Samakan terminologi "myocardial injury" vs "acute myocardial injury"; tambahkan keywords MeSH ("type 2 myocardial infarction", "self-controlled case series").
8. Sinkronkan ke docx final dengan tracked changes.

## Tahap 5 — Struktural (S1, S2, S3)

1. **S1**: Bukan tindakan yang bisa dieksekusi langsung (perlu user merekrut co-author manusia). Catat sebagai action item terpisah untuk user, bukan bagian draf docx.
2. **S2**: Tulis rekomendasi target jurnal (ERJ Perspective atau AJRCCM Perspectives sebagai prioritas, alternatif Chest/Thorax/JACC: Advances/ERJ Open Research; catatan bahwa §8 bisa berdiri sendiri sebagai Viewpoint kardiologi) sebagai bagian pendek di deliverable terpisah.
3. **S3**: Susun response letter (`Manuskrip/Response_Letter.docx` atau serupa) menjawab 8 pertanyaan reviewer satu per satu dengan kutipan sumber; C1 dan C2 dikonfirmasi eksplisit sebagai koreksi yang diakui, bukan diselipkan.

## Deliverables akhir

- `Manuskrip/COPD_ACS_Two_Clock_Model_Review_REVISED.docx` — manuskrip revisi lengkap dengan tracked changes, gambar `image1.png` dan struktur tabel dipertahankan.
- Brief redesain central illustration (dokumen terpisah).
- Supplementary Methods (search string, tanggal, database, pernyataan SANRA).
- Response letter menjawab 8 pertanyaan reviewer.
- Rekomendasi target jurnal singkat.

## Verifikasi sebelum menyatakan tahap selesai

- Walk-through checklist: semua 33 item di-cross-check status "addressed" terhadap teks final, bukan hanya diklaim.
- Cek tidak ada em dash tersisa (`grep` untuk karakter — di teks ekstraksi docx).
- Jalankan quick-check stop-slop (adverb, passive voice, "not X it's Y", tiga kalimat panjang sama, penutup paragraf punchy) pada bagian yang ditulis ulang.
- Cek tidak ada penanda `[to be verified]`/`[to be completed]` tersisa di daftar pustaka.
- Cek konsistensi British English (`randomised`, `hypoxaemia`, dst).
- Konfirmasi `word/media/image1.png` dan seluruh tabel selamat setelah round-trip docx.
- Bandingkan jumlah kata sebelum/sesudah untuk validasi target pangkas ~20% di P3 (memperhitungkan penambahan konten Tahap 2-3 yang memperluas naskah).
