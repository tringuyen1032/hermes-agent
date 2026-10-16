# Bộ ngôn ngữ Tiếng Việt (vi)

Công cụ tạo và cập nhật bản dịch tiếng Việt cho Hermes: desktop, plugin desktop (kanban, bot),
TUI, CLI/gateway (core) và bảng điều khiển web. Bản dịch do mô hình `gpt-6-luna` tạo qua
CLIProxyAPI. Các tệp được sinh ra:

| Bề mặt | Tệp |
|---|---|
| Desktop | `apps/desktop/src/i18n/vi.ts`, `intro-vi.ts` |
| Plugin desktop | khối `vi` trong `plugins/kanban/i18n.ts`, `plugins/hermes-bots/i18n.ts`, `canonical-group-locales.ts` |
| CLI / gateway | `locales/vi.yaml` |
| TUI | `locales/vi.tui.yaml` |
| Web | `web/src/i18n/vi.ts` |

## Cập nhật sau khi đồng bộ upstream

```sh
npm ci                      # ở thư mục gốc repo
scripts/i18n_vi/update.sh   # chỉ dịch chuỗi mới hoặc đã đổi; bản dịch cũ lấy từ cache/
```

Endpoint: `VI_I18N_BASE_URL` + `VI_I18N_API_KEY` (máy chủ tương thích OpenAI, ví dụ CLIProxyAPI).
Nếu không đặt, công cụ dùng provider của Codex CLI trong `~/.codex/config.toml`.
Mô hình: `VI_I18N_MODEL` (mặc định `gpt-6-luna`).

## Sửa tay một bản dịch

`cache/` là bộ nhớ dịch. Ghim bản dịch đã duyệt vào cache rồi chạy lại `update.sh`:

```sh
cd scripts/i18n_vi
uv run --no-project --with pyyaml python override.py desktop-text firstRun.intro.plan "…"
```

Tên cache: `core`, `tui`, `desktop-text`, `desktop-code`, `desktop-intro`, `kanban-text`,
`kanban-code`, `bots-text`, `bots-code`, `canonical-text`, `web-text`, `web-code`.

## Những gì được giữ nguyên

- Tên lệnh (`/new`, `hermes config set …`), cờ, khóa cấu hình, biến môi trường, đường dẫn, URL,
  placeholder (`{name}`, `{0}`, `${…}`) và tên sản phẩm được kiểm tra tự động sau mỗi lần dịch.
- Chuỗi gửi cho mô hình (ví dụ `gateway.kanban.wake.*`) và chuỗi kỹ thuật mà các bản dịch khác
  đều để nguyên tiếng Anh thì giữ tiếng Anh, để không đổi hành vi của agent.
- Hàm dịch (desktop) được chạy thử so với bản tiếng Anh: cùng số tham số, không làm mất đối số,
  giữ nguyên điều kiện và `.filter/.join/...`; chỉ được bỏ logic số nhiều (`n===1`).
- Danh sách từ chấp nhận khi phê duyệt (`approval.inputs.*`) được viết tay: giữ từ tiếng Anh,
  thêm từ tiếng Việt có dấu và không dấu.

## Ngôn ngữ mặc định

Bản build này khởi động bằng Tiếng Việt khi chưa chọn ngôn ngữ
(`apps/desktop/electron/default-ui-locale.ts`). Lần chạy đầu, desktop lưu `display.language: vi`
để CLI, TUI và gateway dùng cùng ngôn ngữ. Đổi lại trong Cài đặt → Giao diện → Ngôn ngữ, hoặc
`hermes config set display.language en`.
