# SymmetricChat
Simple symetrically encrypted chat software
To use the chat you must first fill up your entropy file.
Do this by running entropypool.py and moving around the mouse while recording background noise, more is better.
The mouse movements as their timing (in microseconds) will be combined with the least significant bits of the audio input to create a string of bytes.

Run the server and give people your socket details (IP address and port).
When running the Client you will be asked for a password and username after which you will be connected to the server. 
Type "exit" to quit, hit enter without typing to check for new messages (messages cannot be printed while python is waiting for a text input),
typing anything else will send a message to the server which will forward it to all clients but only the clients with the same key will be able to read it.
Before being sent from the client every message is xor encrypted with the random bytes using them as a onetime pad, and the random bytes will be encrypted with the key and sent alongside the message. It's important not to reuse the noise from the entropypool. Regenerate it again before running the client in future.
When sending the server an encoded message the message preceeds the encrypted random data so some degree of key-dependent transcription would help to obscure it further.
Once the entropy file runs out the client will stop being able to encrypt data as it depends on random numbers to encode the message at this point it will likely crash but I haven't tried it.

This is only a simple demo and improvements could be made at every level.
