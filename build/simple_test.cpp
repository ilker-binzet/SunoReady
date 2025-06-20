
#include <cmath>

extern "C" {
    __declspec(dllexport) double test_function(double x) {
        return x * 2.0;
    }
    
    __declspec(dllexport) int add_numbers(int a, int b) {
        return a + b;
    }
}
