from typing import Any

STRINGS: dict[str, dict[str, str]] = {
    "welcome": {
        "id": "Selamat datang di Jobly! 🇮🇩\nBot pencari kerja pintar untuk Indonesia.\n\nMari kita mulai dengan membuat profil kamu.",
        "en": "Welcome to Jobly! 🇮🇩\nSmart job finder bot for Indonesia.\n\nLet's start by setting up your profile.",
    },
    "ask_name": {
        "id": "Siapa nama lengkap kamu?",
        "en": "What is your full name?",
    },
    "ask_email": {
        "id": "Masukkan alamat email kamu (untuk notifikasi & pemulihan akun):",
        "en": "Enter your email address (for notifications & account recovery):",
    },
    "ask_phone": {
        "id": "Masukkan nomor telepon kamu (opsional, ketik /skip untuk lewati):",
        "en": "Enter your phone number (optional, type /skip to skip):",
    },
    "ask_categories": {
        "id": "Pilih kategori pekerjaan yang kamu minati (bisa pilih lebih dari satu):",
        "en": "Select job categories you're interested in (you can pick multiple):",
    },
    "ask_experience": {
        "id": "Pilih level pengalaman kamu:",
        "en": "Select your experience level:",
    },
    "ask_locations": {
        "id": "Pilih lokasi kerja yang kamu inginkan (bisa pilih lebih dari satu):",
        "en": "Select your preferred work locations (you can pick multiple):",
    },
    "ask_work_arrangement": {
        "id": "Pilih jenis pekerjaan yang kamu inginkan (bisa pilih lebih dari satu):",
        "en": "Select your preferred work arrangements (you can pick multiple):",
    },
    "ask_salary": {
        "id": "Pilih rentang gaji yang kamu harapkan:",
        "en": "Select your expected salary range:",
    },
    "ask_cv": {
        "id": "Upload CV kamu dalam format PDF, atau ketik/paste teks CV kamu langsung.",
        "en": "Upload your CV as a PDF file, or type/paste your CV text directly.",
    },
    "ask_language": {
        "id": "Pilih bahasa untuk bot ini:",
        "en": "Choose the language for this bot:",
    },
    "onboarding_complete": {
        "id": "Profil kamu sudah lengkap! ✅\nKamu mendapat 3 kredit gratis untuk memulai.\n\nJobly akan mengirim notifikasi saat ada lowongan yang cocok.",
        "en": "Your profile is complete! ✅\nYou got 3 free credits to start.\n\nJobly will notify you when matching jobs are found.",
    },
    "profile_summary": {
        "id": "📋 Profil Kamu\n\nNama: {name}\nEmail: {email}\nLevel: {level}\nKategori: {categories}\nLokasi: {locations}\nJenis Kerja: {arrangements}\nKredit: {credits}",
        "en": "📋 Your Profile\n\nName: {name}\nEmail: {email}\nLevel: {level}\nCategories: {categories}\nLocations: {locations}\nArrangements: {arrangements}\nCredits: {credits}",
    },
    "credits_balance": {
        "id": "💰 Saldo kredit kamu: {balance} kredit",
        "en": "💰 Your credit balance: {balance} credits",
    },
    "insufficient_credits": {
        "id": "❌ Kredit kamu tidak cukup. Kamu butuh {needed} kredit.\nGunakan /topup untuk membeli kredit.",
        "en": "❌ Insufficient credits. You need {needed} credit(s).\nUse /topup to buy credits.",
    },
    "tailoring_started": {
        "id": "⏳ Sedang membuat CV yang disesuaikan... Mohon tunggu.",
        "en": "⏳ Tailoring your CV... Please wait.",
    },
    "tailoring_complete": {
        "id": "✅ CV kamu sudah disesuaikan! File dikirim di atas.",
        "en": "✅ Your tailored CV is ready! Files sent above.",
    },
    "cover_letter_started": {
        "id": "⏳ Sedang membuat cover letter... Mohon tunggu.",
        "en": "⏳ Generating your cover letter... Please wait.",
    },
    "cover_letter_complete": {
        "id": "✅ Cover letter kamu sudah siap! File dikirim di atas.",
        "en": "✅ Your cover letter is ready! Files sent above.",
    },
    "topup_menu": {
        "id": "💳 Pilih paket kredit:\n\n⭐ Starter — 5 kredit — Rp 25.000\n🔥 Popular — 15 kredit — Rp 60.000\n💎 Pro — 50 kredit — Rp 150.000\n👑 Bulk — 100 kredit — Rp 250.000",
        "en": "💳 Choose a credit package:\n\n⭐ Starter — 5 credits — Rp 25,000\n🔥 Popular — 15 credits — Rp 60,000\n💎 Pro — 50 credits — Rp 150,000\n👑 Bulk — 100 credits — Rp 250,000",
    },
    "payment_created": {
        "id": "🔗 Klik link di bawah untuk membayar:\n{url}\n\nKredit akan otomatis ditambahkan setelah pembayaran berhasil.",
        "en": "🔗 Click the link below to pay:\n{url}\n\nCredits will be added automatically after payment.",
    },
    "payment_success": {
        "id": "✅ Pembayaran berhasil! {credits} kredit ditambahkan.\nSaldo sekarang: {balance} kredit.",
        "en": "✅ Payment successful! {credits} credits added.\nCurrent balance: {balance} credits.",
    },
    "no_cv_uploaded": {
        "id": "❌ Kamu belum upload CV. Gunakan /upload_cv untuk upload.",
        "en": "❌ No CV uploaded yet. Use /upload_cv to upload one.",
    },
    "cv_uploaded": {
        "id": "✅ CV berhasil diupload dan diproses!",
        "en": "✅ CV uploaded and processed successfully!",
    },
    "help": {
        "id": (
            "📖 Perintah yang tersedia:\n\n"
            "/start — Daftar dan mulai\n"
            "/profile — Lihat profil\n"
            "/edit_preferences — Ubah preferensi\n"
            "/upload_cv — Upload CV baru\n"
            "/credits — Cek saldo kredit\n"
            "/topup — Beli kredit\n"
            "/transactions — Riwayat transaksi\n"
            "/language — Ganti bahasa\n"
            "/help — Tampilkan bantuan\n"
            "/delete_account — Hapus akun"
        ),
        "en": (
            "📖 Available commands:\n\n"
            "/start — Register and start\n"
            "/profile — View your profile\n"
            "/edit_preferences — Change preferences\n"
            "/upload_cv — Upload a new CV\n"
            "/credits — Check credit balance\n"
            "/topup — Buy credits\n"
            "/transactions — Transaction history\n"
            "/language — Switch language\n"
            "/help — Show help\n"
            "/delete_account — Delete your account"
        ),
    },
    "confirm_delete": {
        "id": "⚠️ Apakah kamu yakin ingin menghapus akun? Semua data akan dihapus permanen.",
        "en": "⚠️ Are you sure you want to delete your account? All data will be permanently removed.",
    },
    "account_deleted": {
        "id": "👋 Akun kamu telah dihapus. Terima kasih telah menggunakan Jobly!",
        "en": "👋 Your account has been deleted. Thank you for using Jobly!",
    },
    "already_registered": {
        "id": "Kamu sudah terdaftar! Gunakan /help untuk melihat perintah.",
        "en": "You're already registered! Use /help to see available commands.",
    },
    "not_registered": {
        "id": "Kamu belum terdaftar. Gunakan /start untuk mendaftar.",
        "en": "You're not registered yet. Use /start to sign up.",
    },
    "language_changed": {
        "id": "✅ Bahasa diubah ke Bahasa Indonesia.",
        "en": "✅ Language changed to English.",
    },
    "done_selecting": {
        "id": "✅ Selesai",
        "en": "✅ Done",
    },
    "btn_tailor_cv": {
        "id": "📄 Sesuaikan CV — 1 kredit",
        "en": "📄 Tailor CV — 1 credit",
    },
    "btn_cover_letter": {
        "id": "✉️ Cover Letter — 1 kredit",
        "en": "✉️ Cover Letter — 1 credit",
    },
    "btn_view_original": {
        "id": "🔗 Lihat Asli",
        "en": "🔗 View Original",
    },
}


def t(key: str, lang: str = "id", **kwargs: Any) -> str:
    entry = STRINGS.get(key, {})
    text = entry.get(lang, entry.get("id", f"[missing:{key}]"))
    if kwargs:
        text = text.format(**kwargs)
    return text
