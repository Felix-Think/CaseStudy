<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="utf-8" />
  <title></title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="/static/styles.css" />
</head>
<body class="app-body">
  <div class="app-bg"></div>

  <!-- App layout: Sidebar + Main -->
  <div id="app" class="chat-shell" role="application">

    <!-- Sidebar: conversation list -->
    <aside id="sidebar" class="chat-sidebar" aria-label="Danh sách hội thoại">
      <header class="chat-sidebar__head">
        <div class="chat-sidebar__title">
          <h1>ChatGPT</h1>
          <a class="btn btn--ghost" href="index.html">← Về CaseStudy</a>
        </div>
        <form class="chat-sidebar__new" action="#" method="get" aria-label="Tạo hội thoại mới">
          <button class="btn btn--primary" type="submit">+ Cuộc trò chuyện mới</button>
        </form>
      </header>

      <nav aria-label="Hội thoại gần đây">
        <ul>
          <li>
            <a href="#" aria-current="page">Học Django cơ bản</a>
            <small>Hôm nay • 14:02</small>
          </li>
          <li>
            <a href="#">Face ID chống giả mạo</a>
            <small>Hôm qua • 21:18</small>
          </li>
          <li>
            <a href="#">Lộ trình Python Dev</a>
            <small>Chủ nhật • 10:35</small>
          </li>
        </ul>
      </nav>

      <section aria-label="Bộ sưu tập & cài đặt">
        <details>
          <summary>Mục đã lưu</summary>
          <ul>
            <li><a href="#">Prompt mẫu: Viết test</a></li>
            <li><a href="#">Mẫu rubric chấm điểm</a></li>
          </ul>
        </details>
        <details>
          <summary>Cài đặt</summary>
          <form action="#" method="post">
            <label for="model">Mô hình</label>
            <select id="model" name="model">
              <option>GPT-5 Thinking</option>
              <option>GPT-4o</option>
              <option>Mini</option>
            </select>
            <br />
            <label><input type="checkbox" name="code_wrap" /> Tự xuống dòng code</label>
            <br />
            <button type="submit">Lưu</button>
          </form>
        </details>
      </section>
    </aside>

    <!-- Main content: chat thread -->
    <main id="chat" class="chat-main" aria-label="Cuộc trò chuyện">
      <!-- Header -->
      <header class="chat-main__head">
        <div>
          <h2>Học Django cơ bản</h2>
          <p>Phiên trò chuyện hiện tại</p>
        </div>
        <form class="chat-main__actions" action="#" method="post" aria-label="Thao tác hội thoại">
          <button type="submit" name="rename">Đổi tên</button>
          <button type="submit" name="share">Chia sẻ</button>
          <button type="submit" name="delete">Xoá</button>
        </form>
      </header>

      <!-- Transcript -->
      <section class="chat-transcript" aria-live="polite" aria-atomic="false">
        <article aria-label="Tin nhắn của Trợ lý">
          <header><strong>Assistant</strong> • 14:02</header>
          <div>
            <p>Chào bạn! Mình có thể giúp xây một API CRUD trong Django Rest Framework. Bạn đang ở bước nào?</p>
            <figure>
              <figcaption>Tóm tắt</figcaption>
              <ul>
                <li>Khởi tạo dự án</li>
                <li>Tạo app & model</li>
                <li>Serializer + ViewSet + Router</li>
              </ul>
            </figure>
          </div>
        </article>

        <article aria-label="Tin nhắn của Bạn">
          <header><strong>Bạn</strong> • 14:03</header>
          <div>
            <p>Mình đã tạo project và app rồi, giờ kết nối MongoDB như thế nào?</p>
          </div>
        </article>

        <article aria-label="Tin nhắn của Trợ lý">
          <header><strong>Assistant</strong> • 14:05</header>
          <div>
            <p>Để dùng MongoDB, bạn có thể dùng <code>djongo</code> hoặc <code>mongoengine</code>. Bạn muốn ORM thuần Django hay chấp nhận ODM?</p>
            <blockquote>Gợi ý: Với ODM, bạn sẽ thao tác model phong cách Mongo thuận tiện hơn.</blockquote>
          </div>
        </article>
      </section>

      <!-- Composer -->
      <footer class="chat-composer" aria-label="Vùng nhập tin nhắn">
        <form action="#" method="post">
          <label for="message">Tin nhắn</label>
          <textarea id="message" name="message" rows="3" placeholder="Nhập nội dung để hỏi..."></textarea>

          <fieldset>
            <legend>Tuỳ chọn đính kèm</legend>
            <label for="file">Tệp</label>
            <input id="file" type="file" name="attachment" />
            <label for="image">Ảnh</label>
            <input id="image" type="file" name="image" accept="image/*" />
          </fieldset>

          <div class="chat-composer__toggles">
            <label>
              <input type="checkbox" name="use_system_prompt" />
              Dùng system prompt mặc định
            </label>
            <label>
              <input type="checkbox" name="stream_mode" />
              Stream câu trả lời
            </label>
          </div>

          <div class="chat-composer__actions">
            <button class="btn btn--primary" type="submit">Gửi</button>
            <button class="btn btn--ghost" type="reset">Xoá</button>
          </div>
        </form>

        <!-- Hints -->
        <section class="chat-hints" aria-label="Gợi ý nhanh">
          <ul>
            <li><button type="button">Tạo API CRUD</button></li>
            <li><button type="button">Viết unit test</button></li>
            <li><button type="button">Sinh dữ liệu mẫu</button></li>
          </ul>
        </section>
      </footer>
    </main>

  </div>

  <!-- Dialogs / Modals (HTML-only placeholders) -->
  <section aria-label="Hộp thoại chia sẻ" hidden>
    <h3>Chia sẻ hội thoại</h3>
    <form action="#" method="post">
      <label for="share-link">Liên kết chia sẻ</label>
      <input id="share-link" type="url" value="https://example.com/chat/abc123" />
      <button type="submit">Sao chép</button>
    </form>
  </section>

</body>
</html>
