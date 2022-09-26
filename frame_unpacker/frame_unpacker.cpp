#include <iostream>
#include <chrono>
using namespace std;
using namespace std::chrono;

int main() {
    auto start = high_resolution_clock::now();

	char chunk[3];
	char _[30];
    size_t bytes_actual;

	freopen(NULL, "rb", stdin);

	for (int row = 0; row < 1520; row++){

		for (int i = 0; i < 1014; i++){
			bytes_actual = fread(chunk, 1, 3, stdin);

			if (bytes_actual != 3) {
				cerr << "Error - Not enough bytes" << endl;
				exit(0);
			}

			unsigned char Pixel_1_a = (chunk[0] >> 6) & 0b00000011;
			unsigned char Pixel_1_b = ((chunk[0] << 2) & 0b11111100) | ((chunk[4] >> 6) & 0b00000011);

			unsigned char Pixel_2_a = (chunk[1] >> 6) & 0b00000011;
			unsigned char Pixel_2_b = ((chunk[1] << 2) & 0b11111100) | ((chunk[4] >> 4) & 0b00000011);

			unsigned char Pixel_3_a = (chunk[2] >> 6) & 0b00000011;
			unsigned char Pixel_3_b = ((chunk[2] << 2) & 0b11111100) | ((chunk[4] >> 2) & 0b00000011);

			unsigned char Pixel_4_a = (chunk[3] >> 6) & 0b00000011;
			unsigned char Pixel_4_b = ((chunk[3] << 2) & 0b11111100) | (chunk[4] & 0b00000011);

			cout << Pixel_1_b << Pixel_1_a;
			cout << Pixel_2_b << Pixel_2_a;
			cout << Pixel_3_b << Pixel_3_a;
			cout << Pixel_4_b << Pixel_4_a;
		}

		fread(_, 1, 30, stdin);
	}

    auto stop = high_resolution_clock::now();
    auto duration = duration_cast<milliseconds>(stop - start);

    cerr << "Unpacked Frame in " << duration.count() << " ms" << endl;
}
