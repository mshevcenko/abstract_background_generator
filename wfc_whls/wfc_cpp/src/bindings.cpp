#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include "wfc.hpp"
#include "overlapping_wfc.hpp"
#include "utils/array_2d.hpp"

namespace py = pybind11;

// Binding code
PYBIND11_MODULE(wfc_cpp, m) {
    m.doc() = "Wave Function Collapse Module";

    // Binding Array2D Class Template (for int type)
    py::class_<OverlappingWFC>(m, "OverlappingWFC")
        .def(py::init<const OverlappingWFC::Options&, const Array2D<uint32_t>&>())
        .def("get_output", &OverlappingWFC::get_output)
        .def("run", &OverlappingWFC::run)
        .def("run_overlapping_wfc", &OverlappingWFC::run_overlapping_wfc)
        ;

    // Binding Wave::Heuristic Enum
    py::enum_<Wave::Heuristic>(m, "Heuristic")
        .value("Entropy", Wave::Heuristic::Entropy)
        .value("Scanline", Wave::Heuristic::Scanline)
        .value("MRV", Wave::Heuristic::MRV)
        .export_values();

    // Binding Options Struct
    py::class_<OverlappingWFC::Options>(m, "Options")
        .def(py::init<>())
        .def_readwrite("periodic_input", &OverlappingWFC::Options::periodic_input)
        .def_readwrite("periodic_output", &OverlappingWFC::Options::periodic_output)
        .def_readwrite("i_W", &OverlappingWFC::Options::i_W)
        .def_readwrite("i_H", &OverlappingWFC::Options::i_H)
        .def_readwrite("o_W", &OverlappingWFC::Options::o_W)
        .def_readwrite("o_H", &OverlappingWFC::Options::o_H)
        .def_readwrite("symmetry", &OverlappingWFC::Options::symmetry)
        .def_readwrite("pattern_size", &OverlappingWFC::Options::pattern_size)
        .def_readwrite("heuristic", &OverlappingWFC::Options::heuristic)
        .def_readwrite("ground", &OverlappingWFC::Options::ground)
        ;

    // Binding Array2D Class Template (for uint32_t type)
    py::class_<Array2D<uint32_t>>(m, "Array2Duint32_t")
        .def(py::init<size_t, size_t>())
        .def(py::init<size_t, size_t, uint32_t>())
        .def("get", &Array2D<uint32_t>::get)
        .def("set", &Array2D<uint32_t>::set)
        .def("fill", &Array2D<uint32_t>::fill)
        .def("reflected", &Array2D<uint32_t>::reflected)
        .def("rotated", &Array2D<uint32_t>::rotated)
        .def("__eq__", &Array2D<uint32_t>::operator==)
        .def("__repr__",
            [](const Array2D<uint32_t>& arr) {
                return "<Array2DInt: " + std::to_string(arr.MX) + "x" + std::to_string(arr.MY) + ">";
            }
        )
        .def_static("from_list", [](const std::vector<std::vector<uint32_t>>& input) {
                if (input.empty()) throw std::runtime_error("Input list cannot be empty");

                size_t rows = input.size();
                size_t cols = input[0].size();

                Array2D<uint32_t> result(cols, rows);
                for (size_t y = 0; y < rows; ++y) {
                    if (input[y].size() != cols)
                        throw std::runtime_error("All rows must have the same number of columns");

                    for (size_t x = 0; x < cols; ++x) {
                        result.set(x, y, input[y][x]);
                    }
                }
                return result;
            }
            , "Create an Array2D from a list of lists"
        )
        .def("to_numpy", [](const Array2D<uint32_t>& self) {
                return py::array_t<uint32_t>(
                    { self.MY, self.MX }, // Shape of the array
                    { self.MX * sizeof(uint32_t), sizeof(uint32_t) }, // Strides
                    self.data.data()  // Pointer to the data
                );
            }
        )
        .def_static("from_numpy", [](const py::array_t<uint32_t>& array) {
                py::buffer_info info = array.request();

                if (info.ndim != 2) {
                    throw std::runtime_error("Input array must be 2D");
                }

                size_t MY = info.shape[0];
                size_t MX = info.shape[1];

                Array2D<uint32_t> result(MX, MY);  // Create Array2D with appropriate dimensions

                auto ptr = static_cast<uint32_t*>(info.ptr);
                std::copy(ptr, ptr + (MX * MY), result.data.begin());  // Copy data into Array2D

                return result;
            }
        )
    ;

    // Binding Array2D Class Template (for std::array<uint8_t, 3> type)
    py::class_<Array2D<std::array<uint8_t, 3>>>(m, "Array2DarrayUint8_3")
        .def(py::init<size_t, size_t>())
        .def(py::init<size_t, size_t, std::array<uint8_t, 3>>())
        .def("get", &Array2D<std::array<uint8_t, 3>>::get)
        .def("set", &Array2D<std::array<uint8_t, 3>>::set)
        .def("fill", &Array2D<std::array<uint8_t, 3>>::fill)
        .def("reflected", &Array2D<std::array<uint8_t, 3>>::reflected)
        .def("rotated", &Array2D<std::array<uint8_t, 3>>::rotated)
        .def("__eq__", &Array2D<std::array<uint8_t, 3>>::operator==)
        .def("__repr__",
            [](const Array2D<std::array<uint8_t, 3>>& arr) {
                return "<Array2DArrayUint8_3: " + std::to_string(arr.MX) + "x" + std::to_string(arr.MY) + ">";
            }
        )
        .def_static("from_list", [](const std::vector<std::vector<std::array<uint8_t, 3>>> &input) {
                if (input.empty()) throw std::runtime_error("Input list cannot be empty");

                size_t rows = input.size();
                size_t cols = input[0].size();

                Array2D<std::array<uint8_t, 3>> result(cols, rows);
                for (size_t y = 0; y < rows; ++y) {
                    if (input[y].size() != cols)
                        throw std::runtime_error("All rows must have the same number of columns");

                    for (size_t x = 0; x < cols; ++x) {
                        result.set(x, y, input[y][x]);
                    }
                }
                return result;
            }
            , "Create an Array2D from a list of lists"
        )
        .def("to_numpy", [](const Array2D<std::array<uint8_t, 3>>& self) {
                return py::array_t<uint8_t>(
                    { self.MY, self.MX, (size_t) 3 }, // Shape of the array (height, width, 3 channels)
                    { self.MX * 3 * sizeof(uint8_t), 3 * sizeof(uint8_t), sizeof(uint8_t) }, // Strides
                    self.data.data()->data()  // Pointer to the data
                );
            }
        )
        .def_static("from_numpy", [](const py::array_t<uint8_t>& array) {
                py::buffer_info info = array.request();

                if (info.ndim != 3 || info.shape[2] != 3) {
                    throw std::runtime_error("Input array must be 3D with 3 channels");
                }

                size_t MY = info.shape[0];
                size_t MX = info.shape[1];

                Array2D<std::array<uint8_t, 3>> result(MX, MY);  // Create Array2D with appropriate dimensions

                auto ptr = static_cast<uint8_t*>(info.ptr);
                for (size_t y = 0; y < MY; ++y) {
                    for (size_t x = 0; x < MX; ++x) {
                        size_t idx = (y * MX + x) * 3;
                        std::array<uint8_t, 3> pixel = { ptr[idx], ptr[idx + 1], ptr[idx + 2] };
                        result.set(x, y, pixel);  // Copy data into Array2D
                    }
                }

                return result;
            }
        )
    ;
}
