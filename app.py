from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder='templates')

# ========== CAESAR CIPHER ==========
def caesar_encrypt(text, shift):
    result = ""
    for ch in text:
        if ch.isalpha():
            base = 65 if ch.isupper() else 97
            result += chr((ord(ch) - base + shift) % 26 + base)
        else:
            result += ch
    return result

def caesar_decrypt(text, shift):
    return caesar_encrypt(text, -shift)

# ========== RAIL FENCE CIPHER ==========
def rail_fence_encrypt(text, rails):
    if rails <= 1:
        return text
    fence = [[] for _ in range(rails)]
    row, direction = 0, 1
    for char in text:
        fence[row].append(char)
        row += direction
        if row == 0 or row == rails - 1:
            direction *= -1
    result = ""
    for rail in fence:
        result += "".join(rail)
    return result

def rail_fence_decrypt(cipher, rails):
    if rails <= 1:
        return cipher
    pattern = [[] for _ in range(rails)]
    row, direction = 0, 1
    for i in range(len(cipher)):
        pattern[row].append(i)
        row += direction
        if row == 0 or row == rails - 1:
            direction *= -1
    result = [""] * len(cipher)
    index = 0
    for rail in pattern:
        for pos in rail:
            result[pos] = cipher[index]
            index += 1
    return "".join(result)

# ========== DIFFIE-HELLMAN ==========
def mod_power(base, exp, mod):
    result = 1
    base %= mod
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod
        base = (base * base) % mod
        exp //= 2
    return result

def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def find_primitive_roots(q):
    roots = []
    required_set = set(range(1, q))
    for g in range(2, q):
        actual_set = set()
        for power in range(1, q):
            actual_set.add(mod_power(g, power, q))
        if actual_set == required_set:
            roots.append(g)
    return roots

# ========== ROUTES ==========
@app.route("/", methods=["GET", "POST"])
def index():
    # Caesar Cipher variables
    caesar_text = ""
    caesar_shift = ""
    caesar_result = ""
    caesar_message = ""
    caesar_result_label = ""
    
    # Rail Fence variables
    rail_text = ""
    rail_rails = ""
    rail_result = ""
    rail_message = ""
    rail_result_label = ""
    
    # Diffie-Hellman variables
    dh_q = ""
    dh_alpha = ""
    dh_xa = ""
    dh_xb = ""
    dh_ya = ""
    dh_yb = ""
    dh_ka = ""
    dh_kb = ""
    dh_message = ""
    
    # Get which algorithm was submitted
    algorithm = request.form.get("algorithm", "")
    
    if request.method == "POST":
        if algorithm == "caesar":
            caesar_text = request.form.get("caesar_text", "").strip()
            caesar_shift = request.form.get("caesar_shift", "").strip()
            action = request.form.get("action", "")
            
            if not caesar_text and not caesar_shift:
                caesar_message = "Please enter text and shift value."
            elif not caesar_text:
                caesar_message = "Please enter text."
            elif not caesar_shift:
                caesar_message = "Please enter shift value."
            else:
                try:
                    shift_num = int(caesar_shift)
                    if shift_num < 0 or shift_num > 25:
                        caesar_message = "Shift must be between 0 and 25."
                    else:
                        if action == "encrypt":
                            caesar_result = caesar_encrypt(caesar_text, shift_num)
                            caesar_result_label = "Encrypted Text"
                        elif action == "decrypt":
                            caesar_result = caesar_decrypt(caesar_text, shift_num)
                            caesar_result_label = "Decrypted Text"
                except ValueError:
                    caesar_message = "Shift must be a number."
        
        elif algorithm == "rail":
            rail_text = request.form.get("rail_text", "").strip()
            rail_rails = request.form.get("rail_rails", "").strip()
            action = request.form.get("action", "")
            
            if not rail_text and not rail_rails:
                rail_message = "Please enter text and number of rails."
            elif not rail_text:
                rail_message = "Please enter text."
            elif not rail_rails:
                rail_message = "Please enter number of rails."
            else:
                try:
                    rails_num = int(rail_rails)
                    if rails_num < 2:
                        rail_message = "Rails must be at least 2."
                    elif rails_num >= len(rail_text):
                        rail_message = "Rails must be less than text length."
                    else:
                        if action == "encrypt":
                            rail_result = rail_fence_encrypt(rail_text, rails_num)
                            rail_result_label = "Encrypted Text"
                        elif action == "decrypt":
                            rail_result = rail_fence_decrypt(rail_text, rails_num)
                            rail_result_label = "Decrypted Text"
                except ValueError:
                    rail_message = "Rails must be a number."
        
        elif algorithm == "diffie":
            dh_q = request.form.get("dh_q", "").strip()
            dh_alpha = request.form.get("dh_alpha", "").strip()
            dh_xa = request.form.get("dh_xa", "").strip()
            dh_xb = request.form.get("dh_xb", "").strip()
            
            if not dh_q or not dh_alpha or not dh_xa or not dh_xb:
                dh_message = "Please enter all values."
            else:
                try:
                    q_num = int(dh_q)
                    alpha_num = int(dh_alpha)
                    xa_num = int(dh_xa)
                    xb_num = int(dh_xb)
                    
                    if not is_prime(q_num):
                        dh_message = "q must be a prime number."
                    elif not (1 < xa_num < q_num) or not (1 < xb_num < q_num):
                        dh_message = "Private keys must satisfy: 1 < XA, XB < q"
                    else:
                        dh_ya = mod_power(alpha_num, xa_num, q_num)
                        dh_yb = mod_power(alpha_num, xb_num, q_num)
                        dh_ka = mod_power(dh_yb, xa_num, q_num)
                        dh_kb = mod_power(dh_ya, xb_num, q_num)
                except ValueError:
                    dh_message = "All values must be numbers."
    
    return render_template(
        "index.html",
        # Caesar
        caesar_text=caesar_text, caesar_shift=caesar_shift,
        caesar_result=caesar_result, caesar_message=caesar_message,
        caesar_result_label=caesar_result_label,
        # Rail Fence
        rail_text=rail_text, rail_rails=rail_rails,
        rail_result=rail_result, rail_message=rail_message,
        rail_result_label=rail_result_label,
        # Diffie-Hellman
        dh_q=dh_q, dh_alpha=dh_alpha, dh_xa=dh_xa, dh_xb=dh_xb,
        dh_ya=dh_ya, dh_yb=dh_yb, dh_ka=dh_ka, dh_kb=dh_kb,
        dh_message=dh_message
    )

@app.route("/get_roots", methods=["POST"])
def get_roots():
    data = request.get_json()
    q = int(data.get("q", 0))
    
    if not is_prime(q):
        return jsonify({"error": "q must be a prime number"})
    
    roots = find_primitive_roots(q)
    return jsonify({"roots": roots})

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
