#include <Windows.h>
#include <iostream>
#include <string>
#include <fstream>
#include <sstream>
#include <vector>

#define PATCH_SIZE 6
typedef NTSTATUS(NTAPI* TRtlAdjustPrivilege)(ULONG privilege, BOOLEAN enable, BOOLEAN current_thread, PBOOLEAN enabled);

int main(int argc, char* argv[])
{
//	ShowWindow(GetConsoleWindow(), SW_HIDE);

	std::ofstream f("ExtPatch.txt", std::ofstream::out | std::ofstream::app);

	if (argc != 3)
	{
		f << "Usage: " << argv[0] << " <process_id> <text>" << std::endl;
		return EXIT_FAILURE;
	}
	f << "Target process: " << argv[1] << " Text: " << argv[2] << std::endl;

	auto stNewExt = std::string(argv[2]);

	std::ifstream in("address.txt", std::ios_base::binary);
	if (!in)
	{
		f << "address.txt file is not exist" << std::endl;
		return EXIT_FAILURE;
	}

	in.exceptions(std::ios_base::badbit | std::ios_base::failbit | std::ios_base::eofbit);
	auto stContent = std::string(std::istreambuf_iterator<char>(in), std::istreambuf_iterator<char>());
	if (stContent.empty())
	{
		f << "address.txt file is empty" << std::endl;
		return EXIT_FAILURE;
	}

	std::stringstream ss;
	ss << stContent;

	uintptr_t pAddress = 0;
	ss >> std::hex >> pAddress;

	f << "Target process: " << argv[1] << " Extension: '" << stNewExt << "' Target: " << std::hex << pAddress << "(" << stContent << ")" << std::endl;

	auto hNtdll = LoadLibraryA("ntdll.dll");
	if (!hNtdll)
	{
		f << "LoadLibraryA failed. Error code: " << GetLastError() << std::endl;
		return EXIT_FAILURE;
	}

	auto RtlAdjustPrivilege = reinterpret_cast<TRtlAdjustPrivilege>(GetProcAddress(hNtdll, "RtlAdjustPrivilege"));
	if (!RtlAdjustPrivilege)
	{
		f << "GetProcAddress failed. Error code: " << GetLastError() << std::endl;
		return EXIT_FAILURE;
	}

	BOOLEAN enabled;
	auto ntStatus = RtlAdjustPrivilege(20, TRUE, FALSE, &enabled);
	if (ntStatus != 0)
	{
		f << "RtlAdjustPrivilege failed. Error code: " << std::hex << ntStatus << std::endl;
		return EXIT_FAILURE;
	}

	auto hProcess = OpenProcess(PROCESS_VM_WRITE | PROCESS_VM_OPERATION, FALSE, std::stoul(argv[1]));
	if (!hProcess || hProcess == INVALID_HANDLE_VALUE)
	{
		f << "OpenProcess failed. Error code: " << GetLastError() << std::endl;
		return EXIT_FAILURE;
	}

	auto dwOldProtect = 0UL;
	if (!VirtualProtectEx(hProcess, reinterpret_cast<LPVOID>(pAddress), PATCH_SIZE, PAGE_EXECUTE_READWRITE, &dwOldProtect))
	{
		f << "VirtualProtectEx(pre) failed. Error code: " << GetLastError() << std::endl;
		return EXIT_FAILURE;
	}

	SIZE_T cbWritten = 0;
	if (!WriteProcessMemory(hProcess, reinterpret_cast<LPVOID>(pAddress), stNewExt.c_str(), stNewExt.size(), &cbWritten) || cbWritten != stNewExt.size())
	{
		f << "WriteProcessMemory failed. Error code: " << GetLastError() << " Written size : " << cbWritten << std::endl;
		return EXIT_FAILURE;
	}

	const uint8_t pNullByte = { 0x0 };
	for (auto i = 0U; i < PATCH_SIZE - stNewExt.size(); ++i)
	{
		auto pTargetAddr = reinterpret_cast<LPVOID>(pAddress + stNewExt.size() + i);
		if (!WriteProcessMemory(hProcess, pTargetAddr, &pNullByte, 1, &cbWritten))
		{
			f << "WriteProcessMemory(sub " << i << ") failed. Error code: " << GetLastError() << " Target : " << std::hex << pTargetAddr << std::endl;
			return EXIT_FAILURE;
		}
	}

	if (!VirtualProtectEx(hProcess, reinterpret_cast<LPVOID>(pAddress), PATCH_SIZE, dwOldProtect, &dwOldProtect))
	{
		f << "VirtualProtectEx(post) failed. Error code: " << GetLastError() << std::endl;
		return EXIT_FAILURE;
	}

	f.close();
	CloseHandle(hProcess);
	f << "completed" << std::endl;
	return EXIT_SUCCESS;
}
