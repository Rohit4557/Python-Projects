import random
import string

class Secret:
    def _generate_random_characters(self):
        all_chars = string.ascii_letters + string.digits
        result = ''.join(random.choice(all_chars) for _ in range(3))
        return list(result)

    def code(self, mssg):
        '''encrypts the message'''
        length = len(mssg)
        if length < 5:
            return mssg[::-1]
        else:
            mssg = list(mssg)
            a = mssg[-1]
            for i in range(length - 1, 0, -1):
                mssg[i] = mssg[i - 1]
            mssg[0] = a
            r1 = self._generate_random_characters()
            r2 = self._generate_random_characters()
            final_mssg = r1 + mssg + r2
            return ''.join(final_mssg)

    def decode(self, mssg, password):
        correct_password = 1234
        attempt = 3

        while attempt > 0:
            if password == correct_password:
                # Remove random characters from both ends
                mssg = mssg[3:-3]
                mssg = list(mssg)

                # Undo rotation: move first character to the end
                first = mssg[0]
                for i in range(len(mssg) - 1):
                    mssg[i] = mssg[i + 1]
                mssg[-1] = first

                return ''.join(mssg)
            else:
                attempt -= 1
                print("Incorrect password!")
                print(f"Attempts left: {attempt}")
                if attempt == 0:
                    return "Access denied"
                password = int(input("Re-enter password: "))  # Optional interaction

# Testing
c1 = Secret()
encoded = c1.code("Nautiyal")
print("Encoded:", encoded)

decoded = c1.decode(encoded, 134)
print("Decoded:", decoded)
