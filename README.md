# to-single-header
Single `.py` file to inline the contents of a `.h` file from an `#include` directive.
Works best for a simple `stdafx.h`-like file or a header-only library.

## Usage
Run via command line `python to_single_header_tool.py [input_file_path] [output_file_path] [flags]...`. Executing without flags will move `#include` directives found within `.h` files to the top of the output file, as well as remove header guards of the pattern `#ifndef #define #endif` or `#pragma once`.  
※ Will not remove header guards of the pattern `#if !defined() #define #endif`.

| Flag            | Output                                                  |
| :-------------: | :-----------------------------------------------------: |
| `KEEP_INCLUDES` | Disables moving include directives to top as a comment  |
| `KEEP_GUARDS`   | Disables removing header guards or `#pragma once`       |
| `EXTRA_INFO`    | Include path to inlined header file above its placement |

## Example usage
`StdAfx.h` includes
* `stdio.h`
* `utils.h`
* `GraphicsRenderer.h`


`utils.h`:
```cpp
#ifndef UTILS_H
#define UTILS_H

#include <type_traits>

template<typename T>
constexpr bool is_gpu_writable_structure()
	{ return std::is_trivially_copyable_v<T> && std::is_standard_layout_v<T> && !(sizeof(T) % 16); }

#endif // !UTILS_H
```

`GraphicsRenderer.h`:
```cpp
#pragma once
#include <iostream>

#ifdef _WIN32
#include <Windows.h>
using WindowObject = HWND;
#else
using WindowObject = uint64_t;
#endif // _WIN32

template <class D>
class GraphicsRenderer {
protected:
	WindowObject m_wndObject;

	GraphicsRenderer() : m_wndObject(0) { }

public:
	inline void Render() noexcept
		{ static_cast<D*>(this)->RenderImpl(); }

};
```

`StdAfx.h` initially:
```cpp
#ifndef STDAFX_H
#define STDAFX_H

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

#define WIN32_LEAN_AND_MEAN

#include <stdio.h>
#include "utils.h"
#include "GraphicsRenderer.h"

#endif // !STDAFX_H
```

Output `StdAfx.h` inlined includes with flags `0`:
```cpp
// parser notes will be put here if any:
// include directive found at l3 in utils.h
// #include <type_traits>
// 
// include directive found at l1 in GraphicsRenderer.h
// #include <iostream>
// 
// include directive found at l4 in GraphicsRenderer.h
// #include <Windows.h>
// 
// 

#ifndef STDAFX_H
#define STDAFX_H

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

#define WIN32_LEAN_AND_MEAN

#include <stdio.h>
template<typename T>
constexpr bool is_gpu_writable_structure()
	{ return std::is_trivially_copyable_v<T> && std::is_standard_layout_v<T> && !(sizeof(T) % 16); }

#ifdef _WIN32
using WindowObject = HWND;
#else
using WindowObject = uint64_t;
#endif // _WIN32

template <class D>
class GraphicsRenderer {
protected:
	WindowObject m_wndObject;

	GraphicsRenderer() : m_wndObject(0) { }

public:
	inline void Render() noexcept
		{ static_cast<D*>(this)->RenderImpl(); }

};


#endif // !STDAFX_H

```

Output `StdAfx.h` inlined includes with flags `EXTRA_INFO`:
```cpp
// parser notes will be put here if any:
// include directive found at l3 in utils.h
// #include <type_traits>
// 
// include directive found at l1 in GraphicsRenderer.h
// #include <iostream>
// 
// include directive found at l4 in GraphicsRenderer.h
// #include <Windows.h>
// 
// 

#ifndef STDAFX_H
#define STDAFX_H

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

#define WIN32_LEAN_AND_MEAN

#include <stdio.h>
// utils.h


template<typename T>
constexpr bool is_gpu_writable_structure()
	{ return std::is_trivially_copyable_v<T> && std::is_standard_layout_v<T> && !(sizeof(T) % 16); }

// GraphicsRenderer.h

#ifdef _WIN32
using WindowObject = HWND;
#else
using WindowObject = uint64_t;
#endif // _WIN32

template <class D>
class GraphicsRenderer {
protected:
	WindowObject m_wndObject;

	GraphicsRenderer() : m_wndObject(0) { }

public:
	inline void Render() noexcept
		{ static_cast<D*>(this)->RenderImpl(); }

};


#endif // !STDAFX_H

```
