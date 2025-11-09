const chatbox = document.getElementById("chatbox");
const input = document.getElementById("input");
const send = document.getElementById("send");

send.addEventListener("click", async () => {
    const ref = input.value.trim();
    if (!ref) return;

    // Kullanıcı mesajını ekle
    chatbox.innerHTML += `<div class="user">Sen: ${ref}</div>`;

    try {
        const res = await fetch(`/messages?ref=${encodeURIComponent(ref)}`);
        const data = await res.json();

        if (data.found) {
            chatbox.innerHTML += `<div class="bot">Bot: ${data.message}</div>`;
        } else {
            chatbox.innerHTML += `<div class="bot">Bot: Bu referans kodu ile eşleşen mesaj bulunamadı.</div>`;
        }
    } catch (err) {
        chatbox.innerHTML += `<div class="bot">Bot: Hata oluştu: ${err}</div>`;
    }

    chatbox.scrollTop = chatbox.scrollHeight;
    input.value = "";
});
