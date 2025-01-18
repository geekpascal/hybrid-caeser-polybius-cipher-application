from flask import Flask, render_template, request, jsonify
import string
import re

app = Flask(__name__)

def generate_polybius_square(keyword):
    alphabet = string.ascii_uppercase
    keyword = ''.join(dict.fromkeys(keyword.upper()))
    remaining_letters = ''.join(letter for letter in alphabet if letter not in keyword)
    polybius_square = keyword + remaining_letters
    return polybius_square

def is_encrypted_format(text):
    # Check if the text consists of number pairs (encrypted format)
    number_pairs = re.findall(r'\d{2}', text)
    return len(number_pairs) > 0 and all(11 <= int(pair) <= 55 for pair in number_pairs)

def encrypt(message, caesar_shift, polybius_keyword):
    polybius_square = generate_polybius_square(polybius_keyword)
    encrypted = ""
    
    for char in message:
        if char.isalpha():
            # Convert to uppercase for processing
            upper_char = char.upper()
            
            # Caesar cipher
            shifted_char = chr((ord(upper_char) - 65 + caesar_shift) % 26 + 65)
            
            # Polybius cipher
            index = polybius_square.index(shifted_char)
            row, col = divmod(index, 5)
            encrypted += f"{row+1}{col+1}"
        else:
            # For non-alphabetic characters, add a special marker
            encrypted += f"00{ord(char):03}"
    
    return encrypted

def decrypt(message, caesar_shift, polybius_keyword):
    polybius_square = generate_polybius_square(polybius_keyword)
    decrypted = ""
    i = 0
    
    while i < len(message):
        if i + 1 < len(message) and message[i:i+2].isdigit():
            if message[i:i+2] == "00" and i + 4 < len(message):
                # Handle non-alphabetic characters
                try:
                    char_code = int(message[i+2:i+5])
                    decrypted += chr(char_code)
                    i += 5
                    continue
                except ValueError:
                    pass
            
            try:
                row, col = int(message[i]) - 1, int(message[i+1]) - 1
                if 0 <= row < 5 and 0 <= col < 5:
                    char = polybius_square[row * 5 + col]
                    # Reverse Caesar cipher
                    decrypted_char = chr((ord(char) - 65 - caesar_shift) % 26 + 65)
                    decrypted += decrypted_char
                    i += 2
                    continue
            except ValueError:
                pass
        
        # If we reach here, treat the current character as regular text
        decrypted += message[i]
        i += 1
    
    return decrypted

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encrypt', methods=['POST'])
def encrypt_message():
    data = request.json
    message = data['message']
    caesar_shift = int(data['caesarShift'])
    polybius_keyword = data['polybiusKeyword']
    
    if is_encrypted_format(message):
        # If the message is already in encrypted format, decrypt it first
        decrypted = decrypt(message, caesar_shift, polybius_keyword)
        encrypted = encrypt(decrypted, caesar_shift, polybius_keyword)
    else:
        encrypted = encrypt(message, caesar_shift, polybius_keyword)
    
    return jsonify({'result': encrypted})

@app.route('/decrypt', methods=['POST'])
def decrypt_message():
    data = request.json
    message = data['message']
    caesar_shift = int(data['caesarShift'])
    polybius_keyword = data['polybiusKeyword']
    decrypted = decrypt(message, caesar_shift, polybius_keyword)
    return jsonify({'result': decrypted})

if __name__ == '__main__':
    app.run(debug=True)
