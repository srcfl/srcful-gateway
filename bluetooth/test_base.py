import base58 

string = bytes("Hello World", "utf-8")

encoded = base58.b58encode(string)

decoded = base58.b58decode(encoded.decode('utf-8'))

# decoded_check = base58.b58decode_check(encoded)

print(encoded.decode("utf-8"), type(encoded.decode("utf-8")))
print(decoded)
# print(decoded_check)