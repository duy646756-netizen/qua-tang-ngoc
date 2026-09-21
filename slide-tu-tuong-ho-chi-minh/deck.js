const pptxgen = require("pptxgenjs");
const P = { RED:"8C0D14", RED2:"B3181F", REDL:"FBEDEC", GOLD:"E8B02B", GOLDL:"FBF1D8",
            INK:"241A16", GRAY:"6E6257", WHITE:"FFFFFF", LINE:"E4DAD0" };
const HF = "Times New Roman", BF = "Arial";
const IMG = "img/";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";            // 13.333 x 7.5
pres.author = "Nhóm 1";
pres.title  = "Tư tưởng Hồ Chí Minh - Nhóm 1";

const W = 13.333;
let pageNo = 1;

function chrome(s, part) {
  pageNo++;
  if (part) s.addText(part, { x:0.62, y:0.34, w:9.5, h:0.3, isTextBox:true, margin:0,
      fontFace:BF, fontSize:11, bold:true, color:P.GOLD, charSpacing:2 });
  s.addText("NHÓM 1  ·  TƯ TƯỞNG HỒ CHÍ MINH", { x:0.62, y:6.95, w:6, h:0.3, isTextBox:true,
      margin:0, fontFace:BF, fontSize:9.5, color:"A99C90" });
  s.addText(String(pageNo), { x:12.1, y:6.95, w:0.62, h:0.3, isTextBox:true, margin:0,
      fontFace:BF, fontSize:11, bold:true, color:P.RED, align:"right" });
}

function title(s, t, y) {
  s.addImage({ path:IMG+"star_gold.png", x:0.62, y:(y||0.72)+0.10, w:0.34, h:0.34 });
  s.addText(t, { x:1.10, y:y||0.72, w:11.6, h:0.56, isTextBox:true, margin:0,
      fontFace:HF, fontSize:26.5, bold:true, color:P.RED, valign:"middle" });
}

function card(s, o) {
  s.addShape(pres.ShapeType.roundRect, { x:o.x, y:o.y, w:o.w, h:o.h, rectRadius:0.10,
      fill:{ color:o.fill||P.REDL }, line:{ color:o.line||(o.fill||P.REDL), width:1.25 },
      shadow:o.shadow===false?undefined:{ type:"outer", color:"9A8C80", opacity:0.18,
        blur:8, offset:2, angle:90 } });
}

function chip(s, x, y, n, c) {
  s.addShape(pres.ShapeType.ellipse, { x, y, w:0.46, h:0.46, fill:{ color:c||P.RED },
      line:{ color:c||P.RED, width:1 } });
  s.addText(n, { x, y, w:0.46, h:0.46, isTextBox:true, margin:0, fontFace:BF, fontSize:14,
      bold:true, color:P.GOLD, align:"center", valign:"middle" });
}

function bullets(s, items, o) {
  s.addText(items.map((t,i) => ({ text:t, options:{ bullet:{ code:"25CF" },
      breakLine:i < items.length-1, color:o.color||P.INK, fontSize:o.fontSize||14.5,
      fontFace:BF, paraSpaceAfter:o.gap===undefined?9:o.gap } })),
    { x:o.x, y:o.y, w:o.w, h:o.h, isTextBox:true, margin:0, valign:"top", lineSpacing:o.ls||21 });
}

function quote(s, o) {
  card(s, { x:o.x, y:o.y, w:o.w, h:o.h, fill:o.fill||P.GOLDL, line:o.line||P.GOLD });
  s.addText("“"+o.text+"”", { x:o.x+0.30, y:o.y+0.16, w:o.w-0.60, h:o.h-0.72, isTextBox:true,
      margin:0, fontFace:HF, fontSize:o.fs||15, italic:true, color:o.tc||P.INK, valign:"middle",
      lineSpacing:o.ls||22 });
  s.addText("— "+o.src, { x:o.x+0.30, y:o.y+o.h-0.54, w:o.w-0.60, h:0.34, isTextBox:true,
      margin:0, fontFace:BF, fontSize:10.5, bold:true, color:o.sc||P.RED, align:"right" });
}

/* ───────────────────────── 1. BÌA ───────────────────────── */
{
  const s = pres.addSlide();
  s.background = { path:IMG+"bg_title.png" };
  s.addText("MÔN HỌC: TƯ TƯỞNG HỒ CHÍ MINH", { x:0.85, y:0.62, w:8.6, h:0.34, isTextBox:true,
      margin:0, fontFace:BF, fontSize:13, bold:true, color:P.GOLD, charSpacing:3 });
  s.addText("BÀI THẢO LUẬN NHÓM 1", { x:0.85, y:1.02, w:8.6, h:0.4, isTextBox:true, margin:0,
      fontFace:BF, fontSize:16, color:"F2D9A8" });
  s.addText("QUÁ TRÌNH NHẬN THỨC\nCỦA ĐẢNG CỘNG SẢN VIỆT NAM\nVỀ TƯ TƯỞNG HỒ CHÍ MINH",
    { x:0.85, y:1.62, w:9.3, h:2.35, isTextBox:true, margin:0, fontFace:HF, fontSize:38,
      bold:true, color:P.WHITE, lineSpacing:46 });
  s.addText("Qua nhận thức nội hàm khái niệm tư tưởng Hồ Chí Minh, hãy đưa ra nhận xét về quá trình nhận thức của Đảng Cộng sản Việt Nam về tư tưởng Hồ Chí Minh.",
    { x:0.85, y:4.08, w:8.9, h:0.8, isTextBox:true, margin:0, fontFace:HF, fontSize:14.5,
      italic:true, color:"F0CFCF", lineSpacing:21 });
  s.addShape(pres.ShapeType.roundRect, { x:0.85, y:5.10, w:11.0, h:1.62, rectRadius:0.10,
      fill:{ color:"6E080F" }, line:{ color:"A8571C", width:1.25 } });
  s.addText("NHÓM 1 — 9 THÀNH VIÊN", { x:1.10, y:5.24, w:5.0, h:0.32, isTextBox:true, margin:0,
      fontFace:BF, fontSize:12, bold:true, color:P.GOLD, charSpacing:1.5 });
  const mem = [["1. Đào Vũ Hoàng Anh","2. Hoàng Đức Anh","3. Nguyễn Sỹ Duy Anh"],
               ["4. Vũ Hoàng Anh","5. Nguyễn Hoàng Công","6. Nguyễn Thành Đạt  (Trưởng nhóm)"],
               ["7. Nguyễn Mai Dương","8. Đặng Tiến Duy","9. Nguyễn Đức Duy"]];
  [0,1,2].forEach(c => s.addText(mem.map(r=>r[c]).join("\n"),
    { x:1.10+c*3.55, y:5.62, w:3.45, h:1.0, isTextBox:true, margin:0, fontFace:BF,
      fontSize:11.5, color:"FBE9E4", lineSpacing:17 }));
  s.addNotes("Chào thầy/cô và các bạn. Nhóm 1 xin trình bày câu hỏi thảo luận: qua nhận thức nội hàm khái niệm tư tưởng Hồ Chí Minh, đưa ra nhận xét về quá trình nhận thức của Đảng Cộng sản Việt Nam về tư tưởng Hồ Chí Minh. Bài gồm 13 slide, thời lượng khoảng 12-15 phút, cuối bài nhóm có 2 câu hỏi thảo luận.");
}

/* ───────────────────────── 2. MỤC LỤC ───────────────────── */
{
  const s = pres.addSlide(); chrome(s, "CẤU TRÚC BÀI TRÌNH BÀY");
  title(s, "NỘI DUNG TRÌNH BÀY");
  s.addImage({ path:IMG+"fig_roadmap.png", x:0.55, y:1.80, w:12.23, h:2.25 });
  const cols = [
    ["KHÁI NIỆM & ĐỊNH NGHĨA", "Làm rõ thuật ngữ “tư tưởng”, “nhà tư tưởng” và định nghĩa tư tưởng Hồ Chí Minh trong Cương lĩnh 2011."],
    ["NỘI HÀM KHÁI NIỆM", "Ba lớp nội dung: bản chất khoa học – cách mạng, nguồn gốc hình thành, giá trị – ý nghĩa."],
    ["QUÁ TRÌNH NHẬN THỨC CỦA ĐẢNG", "Bốn giai đoạn từ năm 1930 đến nay, với mốc bước ngoặt là Đại hội VII (6-1991)."],
    ["NHẬN XÉT & THẢO LUẬN", "Đánh giá tính quy luật của quá trình nhận thức, liên hệ sinh viên và 2 câu hỏi thảo luận."]];
  const xs = [0.72, 3.78, 6.83, 9.89];
  cols.forEach((c,i) => {
    s.addText(c[0], { x:xs[i], y:4.12, w:2.75, h:0.62, isTextBox:true, margin:0, fontFace:BF,
      fontSize:13, bold:true, color:P.RED, align:"center", valign:"top", lineSpacing:17 });
    s.addText(c[1], { x:xs[i], y:4.80, w:2.75, h:1.55, isTextBox:true, margin:0, fontFace:BF,
      fontSize:11.5, color:P.GRAY, align:"center", lineSpacing:16 });
  });
  s.addNotes("Bài trình bày đi theo bốn phần. Phần I và II trả lời vế thứ nhất của câu hỏi là nội hàm khái niệm; phần III và IV trả lời vế thứ hai là quá trình nhận thức của Đảng và nhận xét. Logic xuyên suốt: hiểu đúng nội hàm khái niệm thì mới có căn cứ để nhận xét quá trình nhận thức.");
}

/* ──────────── 3. KHÁI NIỆM TƯ TƯỞNG – NHÀ TƯ TƯỞNG ──────── */
{
  const s = pres.addSlide(); chrome(s, "PHẦN I · KHÁI NIỆM & ĐỊNH NGHĨA");
  title(s, "“TƯ TƯỞNG” VÀ “NHÀ TƯ TƯỞNG”");
  card(s, { x:0.62, y:1.52, w:7.05, h:1.72, fill:P.REDL, line:"EBD3D1" });
  chip(s, 0.92, 1.76, "1");
  s.addText("Khái niệm “tư tưởng”", { x:1.52, y:1.76, w:5.9, h:0.34, isTextBox:true, margin:0,
      fontFace:BF, fontSize:14, bold:true, color:P.RED });
  s.addText("Trong cụm từ “tư tưởng Hồ Chí Minh”, “tư tưởng” không hiểu theo nghĩa ý nghĩ của một cá nhân, mà là một hệ thống những quan điểm, quan niệm, luận điểm được xây dựng trên một nền tảng triết học nhất quán, đại biểu cho ý chí, nguyện vọng của một giai cấp, một dân tộc.",
    { x:1.52, y:2.16, w:5.95, h:0.98, isTextBox:true, margin:0, fontFace:BF, fontSize:12.5,
      color:P.INK, lineSpacing:17 });
  card(s, { x:0.62, y:3.40, w:7.05, h:1.52, fill:P.GOLDL, line:"EEDCB0" });
  chip(s, 0.92, 3.64, "2", "A8761A");
  s.addText("Khái niệm “nhà tư tưởng”", { x:1.52, y:3.64, w:5.9, h:0.34, isTextBox:true,
      margin:0, fontFace:BF, fontSize:14, bold:true, color:"8A6A12" });
  s.addText("V.I. Lênin: một người xứng đáng là nhà tư tưởng khi biết giải quyết trước người khác tất cả những vấn đề chính trị – sách lược, các vấn đề về tổ chức, về những yếu tố vật chất của phong trào một cách tự giác.",
    { x:1.52, y:4.04, w:5.95, h:0.78, isTextBox:true, margin:0, fontFace:BF, fontSize:12.5,
      color:P.INK, lineSpacing:17 });
  card(s, { x:0.62, y:5.08, w:7.05, h:1.36, fill:P.RED, line:P.RED });
  s.addText("Hồ Chí Minh hội đủ những tiêu chí đó: Người đã giải quyết thành công những vấn đề cơ bản nhất của cách mạng Việt Nam trong thế kỷ XX — vì vậy tư tưởng của Người là một HỆ THỐNG LÝ LUẬN, không phải những ý kiến rời rạc.",
    { x:0.92, y:5.26, w:6.45, h:1.0, isTextBox:true, margin:0, fontFace:BF, fontSize:12.5,
      color:"FFF2E8", lineSpacing:17 });
  s.addImage({ path:IMG+"fig_tutuong.png", x:7.95, y:1.72, w:5.05, h:4.0 });
  s.addText("Quan hệ: tư tưởng → hệ tư tưởng → nhà tư tưởng",
    { x:7.95, y:5.80, w:5.05, h:0.34, isTextBox:true, margin:0, fontFace:BF, fontSize:10.5,
      color:P.GRAY, align:"center", italic:true });
  s.addNotes("Trước khi nhận xét quá trình nhận thức của Đảng, cần thống nhất cách hiểu thuật ngữ. Điểm mấu chốt: tư tưởng Hồ Chí Minh là một hệ thống lý luận có nền tảng triết học nhất quán, chứ không phải tập hợp những lời nói hay, những mẩu chuyện đạo đức. Chính vì chưa nhận thức được điều này mà trong một thời gian dài Đảng mới chỉ nói tới đạo đức, tác phong Hồ Chủ tịch.");
}

/* ─────────────── 4. ĐỊNH NGHĨA TƯ TƯỞNG HỒ CHÍ MINH ─────── */
{
  const s = pres.addSlide(); chrome(s, "PHẦN I · KHÁI NIỆM & ĐỊNH NGHĨA");
  title(s, "ĐỊNH NGHĨA TƯ TƯỞNG HỒ CHÍ MINH");
  s.addImage({ path:IMG+"fig_quote.png", x:0.70, y:1.90, w:2.30, h:2.30 });
  s.addText("Đại hội XI (2011)\nCương lĩnh xây dựng đất nước trong thời kỳ quá độ lên chủ nghĩa xã hội (bổ sung, phát triển năm 2011)",
    { x:0.62, y:4.40, w:2.46, h:1.5, isTextBox:true, margin:0, fontFace:BF, fontSize:11.5,
      bold:false, color:P.GRAY, align:"center", lineSpacing:16 });
  card(s, { x:3.35, y:1.60, w:9.35, h:3.30, fill:P.REDL, line:"EBD3D1" });
  s.addText("“Tư tưởng Hồ Chí Minh là một hệ thống quan điểm toàn diện và sâu sắc về những vấn đề cơ bản của cách mạng Việt Nam, kết quả của sự vận dụng và phát triển sáng tạo chủ nghĩa Mác – Lênin vào điều kiện cụ thể của nước ta, kế thừa và phát triển các giá trị truyền thống tốt đẹp của dân tộc, tiếp thu tinh hoa văn hoá nhân loại; là tài sản tinh thần vô cùng to lớn và quý giá của Đảng và dân tộc ta, mãi mãi soi đường cho sự nghiệp cách mạng của nhân dân ta giành thắng lợi.”",
    { x:3.68, y:1.84, w:8.72, h:2.55, isTextBox:true, margin:0, fontFace:HF, fontSize:15.5,
      italic:true, color:P.INK, valign:"middle", lineSpacing:24 });
  s.addText("— Văn kiện Đại hội đại biểu toàn quốc lần thứ XI, 2011",
    { x:3.68, y:4.42, w:8.72, h:0.32, isTextBox:true, margin:0, fontFace:BF, fontSize:10.5,
      bold:true, color:P.RED, align:"right" });
  const box = [["3.35","ĐẠI HỘI VII — 6/1991","Lần đầu chính thức nêu khái niệm “tư tưởng Hồ Chí Minh”"],
               ["6.47","ĐẠI HỘI IX — 4/2001","Đưa ra định nghĩa tương đối hoàn chỉnh về tư tưởng Hồ Chí Minh"],
               ["9.58","ĐẠI HỘI XI — 1/2011","Bổ sung, phát triển thành định nghĩa đầy đủ nhất hiện nay"]];
  box.forEach(b => {
    card(s, { x:parseFloat(b[0]), y:5.12, w:3.12, h:1.32, fill:P.WHITE, line:P.LINE });
    s.addText(b[1], { x:parseFloat(b[0])+0.22, y:5.28, w:2.70, h:0.30, isTextBox:true, margin:0,
      fontFace:BF, fontSize:12, bold:true, color:P.RED });
    s.addText(b[2], { x:parseFloat(b[0])+0.22, y:5.62, w:2.70, h:0.70, isTextBox:true, margin:0,
      fontFace:BF, fontSize:11, color:P.GRAY, lineSpacing:15 });
  });
  s.addNotes("Đây là định nghĩa chính thức đang dùng trong giáo trình hiện hành. Ba mốc phía dưới cho thấy ngay bản thân định nghĩa cũng là sản phẩm của một quá trình: 1991 mới nêu khái niệm, 2001 mới có định nghĩa, 2011 mới hoàn chỉnh. Đọc kỹ định nghĩa sẽ thấy nó chứa ba lớp nội hàm mà nhóm phân tích ở ba slide tiếp theo.");
}

/* ─────────── 5. NỘI HÀM (1) BẢN CHẤT & HỆ THỐNG QUAN ĐIỂM ─ */
{
  const s = pres.addSlide(); chrome(s, "PHẦN II · NỘI HÀM KHÁI NIỆM");
  title(s, "NỘI HÀM (1): BẢN CHẤT KHOA HỌC – CÁCH MẠNG");
  const it = [
    ["Là một HỆ THỐNG QUAN ĐIỂM", "có cấu trúc chặt chẽ, logic nhất quán, không phải những luận điểm rời rạc."],
    ["TOÀN DIỆN", "bao quát mọi lĩnh vực: chính trị, kinh tế, văn hoá, quân sự, ngoại giao, đạo đức, con người."],
    ["SÂU SẮC", "chỉ ra bản chất và quy luật vận động của cách mạng Việt Nam, không dừng ở hiện tượng."],
    ["VỀ NHỮNG VẤN ĐỀ CƠ BẢN", "mục tiêu, con đường, lực lượng, phương pháp và tổ chức lực lượng cách mạng."]];
  let y = 1.54;
  it.forEach((b,i) => {
    card(s, { x:0.62, y, w:6.30, h:1.10, fill:i%2 ? P.GOLDL : P.REDL, line:i%2 ? "EEDCB0":"EBD3D1" });
    chip(s, 0.86, y+0.22, String(i+1), i%2 ? "A8761A" : P.RED);
    s.addText(b[0], { x:1.46, y:y+0.18, w:5.30, h:0.32, isTextBox:true, margin:0, fontFace:BF,
      fontSize:13, bold:true, color:i%2 ? "8A6A12" : P.RED });
    s.addText(b[1], { x:1.46, y:y+0.50, w:5.30, h:0.54, isTextBox:true, margin:0, fontFace:BF,
      fontSize:11.5, color:P.INK, lineSpacing:15 });
    y += 1.21;
  });
  s.addText("Cốt lõi xuyên suốt: ĐỘC LẬP DÂN TỘC GẮN LIỀN VỚI CHỦ NGHĨA XÃ HỘI",
    { x:0.62, y:6.34, w:6.30, h:0.36, isTextBox:true, margin:0, fontFace:BF, fontSize:12,
      bold:true, color:P.RED });
  s.addImage({ path:IMG+"fig_hethong.png", x:7.28, y:1.44, w:5.35, h:5.35 });
  s.addNotes("Lớp nội hàm thứ nhất trả lời câu hỏi tư tưởng Hồ Chí Minh LÀ GÌ. Bốn ý ở cột trái chính là bốn từ khoá trong định nghĩa: hệ thống quan điểm - toàn diện - sâu sắc - những vấn đề cơ bản của cách mạng Việt Nam. Sơ đồ bên phải liệt kê các bộ phận cấu thành hệ thống đó. Nhấn mạnh: chính vì là hệ thống nên mới có thể trở thành nền tảng tư tưởng của một Đảng.");
}

/* ───────────────── 6. NỘI HÀM (2) NGUỒN GỐC ─────────────── */
{
  const s = pres.addSlide(); chrome(s, "PHẦN II · NỘI HÀM KHÁI NIỆM");
  title(s, "NỘI HÀM (2): NGUỒN GỐC HÌNH THÀNH");
  s.addImage({ path:IMG+"fig_nguongoc.png", x:5.05, y:1.58, w:7.75, h:4.99 });
  const it = [["Chủ nghĩa Mác – Lênin", "Nguồn gốc lý luận quyết định bản chất khoa học và cách mạng; cung cấp thế giới quan, phương pháp luận. Hồ Chí Minh VẬN DỤNG và PHÁT TRIỂN SÁNG TẠO, không sao chép."],
              ["Giá trị truyền thống dân tộc", "Chủ nghĩa yêu nước, tinh thần đoàn kết, nhân nghĩa, khoan dung, cần cù — là cội nguồn trực tiếp và động lực xuất phát."],
              ["Tinh hoa văn hoá nhân loại", "Văn hoá phương Đông (Nho, Phật) và phương Tây (tư tưởng dân chủ, nhân quyền của cách mạng Pháp, Mỹ)."],
              ["Nhân tố chủ quan Hồ Chí Minh", "Tư duy độc lập, sáng tạo; bản lĩnh kiên định; tâm hồn nhà yêu nước và trải nghiệm thực tiễn 30 năm tìm đường cứu nước."]];
  let y = 1.52;
  it.forEach((b,i) => {
    s.addText(b[0], { x:0.62, y, w:4.28, h:0.30, isTextBox:true, margin:0, fontFace:BF,
      fontSize:13, bold:true, color:i===3 ? "8A6A12" : P.RED });
    s.addText(b[1], { x:0.62, y:y+0.32, w:4.28, h:0.92, isTextBox:true, margin:0, fontFace:BF,
      fontSize:11.6, color:P.INK, lineSpacing:16 });
    y += 1.26;
  });
  s.addNotes("Lớp nội hàm thứ hai trả lời câu hỏi tư tưởng Hồ Chí Minh TỪ ĐÂU MÀ CÓ. Cần nhấn mạnh hai chữ vận dụng và phát triển sáng tạo: đây là điểm phân biệt tư tưởng Hồ Chí Minh với việc sao chép mô hình nước ngoài, và cũng là cơ sở để bác bỏ luận điệu cho rằng tư tưởng Hồ Chí Minh chỉ là bản sao của chủ nghĩa Mác - Lênin.");
}

/* ─────────────── 7. NỘI HÀM (3) GIÁ TRỊ – Ý NGHĨA ───────── */
{
  const s = pres.addSlide(); chrome(s, "PHẦN II · NỘI HÀM KHÁI NIỆM");
  title(s, "NỘI HÀM (3): GIÁ TRỊ VÀ Ý NGHĨA");
  s.addImage({ path:IMG+"fig_giatri.png", x:6.55, y:1.66, w:6.25, h:4.05 });
  bullets(s, [
    "Là TÀI SẢN TINH THẦN VÔ CÙNG TO LỚN VÀ QUÝ GIÁ của Đảng và dân tộc ta — giá trị không chỉ trong quá khứ mà còn cho hiện tại và tương lai.",
    "MÃI MÃI SOI ĐƯỜNG cho sự nghiệp cách mạng của nhân dân ta: đã dẫn dắt thắng lợi của Cách mạng Tháng Tám 1945, hai cuộc kháng chiến và công cuộc đổi mới từ 1986.",
    "Cùng chủ nghĩa Mác – Lênin là NỀN TẢNG TƯ TƯỞNG và KIM CHỈ NAM CHO HÀNH ĐỘNG của Đảng.",
    "Có giá trị quốc tế: năm 1987 UNESCO ra Nghị quyết 24C/18.65 tôn vinh Hồ Chí Minh là Anh hùng giải phóng dân tộc, Nhà văn hoá kiệt xuất của Việt Nam."
  ], { x:0.70, y:1.66, w:5.65, h:3.9, fontSize:13.2, ls:19, gap:11 });
  quote(s, { x:0.62, y:5.66, w:5.80, h:1.06, fs:13.5, ls:19,
    text:"… mãi mãi soi đường cho sự nghiệp cách mạng của nhân dân ta giành thắng lợi.",
    src:"Cương lĩnh 2011" });
  s.addNotes("Lớp nội hàm thứ ba trả lời câu hỏi tư tưởng Hồ Chí Minh CÓ GIÁ TRỊ GÌ. Hai cụm từ cần thuộc: tài sản tinh thần vô cùng to lớn và quý giá, và mãi mãi soi đường. Chữ mãi mãi khẳng định sức sống lâu bền, đây là điểm mới so với định nghĩa năm 2001. Hết phần II, chuyển sang phần III: chính vì nội hàm phong phú như vậy nên Đảng phải trải qua một quá trình dài mới nhận thức được đầy đủ.");
}

/* ───────────────── 8-11. BỐN GIAI ĐOẠN ──────────────────── */
function stage(o) {
  const s = pres.addSlide(); chrome(s, "PHẦN III · QUÁ TRÌNH NHẬN THỨC CỦA ĐẢNG");
  title(s, o.title);
  s.addText(o.lead, { x:0.62, y:1.44, w:12.1, h:0.42, isTextBox:true, margin:0, fontFace:BF,
      fontSize:12.5, italic:true, color:P.GRAY, lineSpacing:17 });
  let x = 0.62;
  o.cards.forEach((c,i) => {
    const w = (12.1 - (o.cards.length-1)*0.28) / o.cards.length;
    card(s, { x, y:1.98, w, h:2.32, fill:c.hl ? P.RED : P.WHITE, line:c.hl ? P.RED : P.LINE });
    s.addText(c.year, { x:x+0.24, y:2.16, w:w-0.48, h:0.34, isTextBox:true, margin:0,
      fontFace:BF, fontSize:13.5, bold:true, color:c.hl ? P.GOLD : P.RED });
    s.addText(c.head, { x:x+0.24, y:2.50, w:w-0.48, h:0.52, isTextBox:true, margin:0,
      fontFace:BF, fontSize:12, bold:true, color:c.hl ? P.WHITE : P.INK, lineSpacing:16 });
    s.addText(c.body, { x:x+0.24, y:3.02, w:w-0.48, h:1.18, isTextBox:true, margin:0,
      fontFace:BF, fontSize:11.3, color:c.hl ? "FBE9E4" : P.GRAY, lineSpacing:15.5 });
    x += w + 0.28;
  });
  if (o.quote) quote(s, { x:0.62, y:4.48, w:7.30, h:1.30, fs:13.2, ls:19,
      text:o.quote.text, src:o.quote.src });
  s.addText(o.note[0], { x:8.20, y:4.48, w:4.52, h:0.30, isTextBox:true, margin:0, fontFace:BF,
      fontSize:12.5, bold:true, color:P.RED });
  s.addText(o.note[1], { x:8.20, y:4.80, w:4.52, h:1.0, isTextBox:true, margin:0, fontFace:BF,
      fontSize:11.5, color:P.INK, lineSpacing:16 });
  s.addImage({ path:IMG+o.strip, x:1.86, y:5.86, w:9.60, h:1.06 });
  s.addNotes(o.notes);
}

stage({ title:"GIAI ĐOẠN 1 (1930 – 1969): VẬN DỤNG TRONG THỰC TIỄN", strip:"fig_tl1.png",
  lead:"Tư tưởng Hồ Chí Minh dẫn dắt cách mạng trên thực tế, nhưng chưa được khái quát thành một hệ thống lý luận mang tên Người.",
  cards:[
    { year:"2/1930", head:"Cương lĩnh chính trị đầu tiên", body:"Do Nguyễn Ái Quốc soạn thảo, xác định con đường cách mạng giải phóng dân tộc gắn với chủ nghĩa xã hội — tư tưởng của Người trở thành ngọn cờ dẫn đường ngay từ khi Đảng ra đời." },
    { year:"1930 – 1941", head:"Có lúc chưa được nhận thức đúng", body:"Chịu ảnh hưởng của khuynh hướng “tả” trong Quốc tế Cộng sản, một số quan điểm sáng tạo của Người từng bị coi là “hữu khuynh”, nặng về dân tộc." },
    { year:"5/1941 – 1945", head:"Trở lại đúng tư tưởng Hồ Chí Minh", body:"Hội nghị Trung ương 8 đặt nhiệm vụ giải phóng dân tộc lên hàng đầu, dẫn tới thắng lợi của Cách mạng Tháng Tám 1945 — thực tiễn kiểm chứng tính đúng đắn." },
    { year:"2/1951", head:"Đại hội II của Đảng", body:"Lần đầu tiên Đảng chính thức đặt vấn đề học tập Hồ Chủ tịch, nhưng mới ở phạm vi đường lối, tác phong và đạo đức.", hl:true }],
  quote:{ text:"Toàn Đảng hãy ra sức học tập đường lối chính trị, tác phong và đạo đức cách mạng của Hồ Chủ tịch.", src:"Văn kiện Đại hội II của Đảng, 2/1951" },
  note:["Nhận xét giai đoạn 1","Nhận thức chủ yếu ở tầng thực tiễn và đạo đức — vận dụng đúng nhưng chưa gọi đúng tên, chưa xem tư tưởng của Người là một hệ thống lý luận độc lập."],
  notes:"Giai đoạn này cho thấy một nghịch lý thú vị: tư tưởng Hồ Chí Minh đã chỉ đạo thực tiễn và đem lại thắng lợi trước khi được nhận thức về mặt lý luận. Cần nhấn mạnh hai chi tiết: giai đoạn 1930-1941 có lúc quan điểm của Người chưa được đánh giá đúng, và chính thực tiễn Cách mạng Tháng Tám đã chứng minh Người đúng. Đại hội II năm 1951 là lần đầu Đảng chính thức kêu gọi học tập Hồ Chủ tịch, nhưng mới dừng ở đường lối, tác phong, đạo đức." });

stage({ title:"GIAI ĐOẠN 2 (1969 – 1986): HỌC TẬP ĐẠO ĐỨC, TÁC PHONG", strip:"fig_tl2.png",
  lead:"Sau khi Chủ tịch Hồ Chí Minh qua đời, Đảng đẩy mạnh học tập và nghiên cứu di sản của Người, nhưng nhận thức lý luận vẫn còn hạn chế.",
  cards:[
    { year:"9/1969", head:"Điếu văn của Ban Chấp hành Trung ương", body:"Khẳng định tầm vóc lịch sử của Người và đặt nhiệm vụ suốt đời học tập đạo đức, tác phong Hồ Chủ tịch." },
    { year:"1976", head:"Đại hội IV", body:"Khẳng định thắng lợi của cách mạng Việt Nam gắn liền với tên tuổi Chủ tịch Hồ Chí Minh; nêu yêu cầu học tập và làm theo gương Người." },
    { year:"1982", head:"Đại hội V", body:"Chủ trương tổ chức học tập một cách có hệ thống tư tưởng, đạo đức, tác phong của Chủ tịch Hồ Chí Minh trong toàn Đảng, toàn dân." },
    { year:"Hạn chế", head:"Chưa thành khái niệm lý luận", body:"Do ảnh hưởng của tư duy chủ quan, duy ý chí và bệnh giáo điều, di sản của Người chủ yếu được nhìn như tấm gương đạo đức, chưa được khái quát thành hệ thống lý luận.", hl:true }],
  quote:{ text:"Dân tộc ta, nhân dân ta, non sông đất nước ta đã sinh ra Hồ Chủ tịch, người anh hùng dân tộc vĩ đại, và chính Người đã làm rạng rỡ dân tộc ta, nhân dân ta và non sông đất nước ta.", src:"Điếu văn của BCH Trung ương Đảng, 9/1969" },
  note:["Nhận xét giai đoạn 2","Nhận thức sâu hơn về tình cảm và đạo đức, nhưng vẫn chưa vượt qua giới hạn: chưa dùng thuật ngữ “tư tưởng Hồ Chí Minh” với tư cách một hệ thống lý luận."],
  notes:"Giai đoạn 1969-1986 là giai đoạn cả nước học tập Bác, nhiều công trình nghiên cứu ra đời, nhưng khái niệm tư tưởng Hồ Chí Minh vẫn chưa xuất hiện trong văn kiện với tư cách một phạm trù lý luận. Nguyên nhân: mô hình tư duy giáo điều, chủ quan duy ý chí thời kỳ trước đổi mới, cộng với quan niệm cho rằng chỉ có chủ nghĩa Mác - Lênin mới là lý luận. Đây chính là hạn chế mà công cuộc đổi mới sẽ khắc phục." });

stage({ title:"GIAI ĐOẠN 3 (1986 – 1991): BƯỚC NGOẶT VỀ NHẬN THỨC", strip:"fig_tl3.png",
  lead:"Đổi mới tư duy lý luận đã dẫn tới bước nhảy vọt: từ chỗ học tập đạo đức, tác phong đến chỗ khẳng định tư tưởng Hồ Chí Minh là nền tảng tư tưởng của Đảng.",
  cards:[
    { year:"12/1986", head:"Đại hội VI — đổi mới tư duy", body:"Đặt yêu cầu nắm vững bản chất cách mạng, khoa học của chủ nghĩa Mác – Lênin và kế thừa di sản tư tưởng, lý luận của Chủ tịch Hồ Chí Minh." },
    { year:"1987 – 1990", head:"UNESCO vinh danh", body:"Nghị quyết 24C/18.65 tôn vinh Hồ Chí Minh là Anh hùng giải phóng dân tộc, Nhà văn hoá kiệt xuất của Việt Nam, kỷ niệm 100 năm ngày sinh (1990)." },
    { year:"6/1991", head:"Đại hội VII — mốc bước ngoặt", body:"Lần đầu tiên chính thức đưa khái niệm “tư tưởng Hồ Chí Minh” vào Văn kiện và Cương lĩnh, xác định đó là nền tảng tư tưởng, kim chỉ nam cho hành động của Đảng.", hl:true }],
  quote:{ text:"Đảng lấy chủ nghĩa Mác – Lênin và tư tưởng Hồ Chí Minh làm nền tảng tư tưởng, kim chỉ nam cho hành động.", src:"Cương lĩnh xây dựng đất nước trong thời kỳ quá độ lên CNXH, 6/1991" },
  note:["Vì sao là bước ngoặt?","Nhận thức chuyển từ TÌNH CẢM – ĐẠO ĐỨC sang LÝ LUẬN KHOA HỌC; tư tưởng Hồ Chí Minh được đặt ngang tầm chủ nghĩa Mác – Lênin trong nền tảng tư tưởng của Đảng."],
  notes:"Đây là slide trọng tâm của phần III. Cần trả lời được: vì sao phải đến 1991 mới khẳng định? Thứ nhất, phải có đổi mới tư duy từ Đại hội VI mới thoát khỏi bệnh giáo điều. Thứ hai, thực tiễn 5 năm đầu đổi mới chứng minh đường lối đúng là đường lối trở về với tư tưởng Hồ Chí Minh. Thứ ba, bối cảnh chủ nghĩa xã hội ở Liên Xô, Đông Âu khủng hoảng đặt ra yêu cầu khẳng định nền tảng tư tưởng riêng, phù hợp Việt Nam. UNESCO vinh danh năm 1987 cũng góp phần khẳng định tầm vóc quốc tế." });

stage({ title:"GIAI ĐOẠN 4 (1991 – NAY): HOÀN THIỆN VÀ PHÁT TRIỂN", strip:"fig_tl4.png",
  lead:"Từ sau Đại hội VII, nhận thức của Đảng tiếp tục được bổ sung, cụ thể hoá và chuyển thành hành động thực tiễn trong toàn Đảng, toàn dân.",
  cards:[
    { year:"4/2001", head:"Đại hội IX", body:"Đưa ra định nghĩa tương đối hoàn chỉnh, xác định rõ nguồn gốc, nội dung và giá trị của tư tưởng Hồ Chí Minh." },
    { year:"1/2011", head:"Đại hội XI", body:"Cương lĩnh (bổ sung, phát triển) hoàn chỉnh định nghĩa: khẳng định tài sản tinh thần vô cùng to lớn, quý giá và mãi mãi soi đường.", hl:true },
    { year:"2006 – 2021", head:"Học tập và làm theo", body:"Chỉ thị 06 (2006) → Chỉ thị 03 (2011) → Chỉ thị 05 (2016) về tư tưởng, đạo đức, phong cách Hồ Chí Minh → Kết luận 01-KL/TW (2021)." },
    { year:"2021", head:"Đại hội XIII", body:"Xác định kiên định và vận dụng, phát triển sáng tạo chủ nghĩa Mác – Lênin, tư tưởng Hồ Chí Minh; đẩy mạnh bảo vệ nền tảng tư tưởng của Đảng." }],
  quote:{ text:"Kiên định và vận dụng, phát triển sáng tạo chủ nghĩa Mác – Lênin, tư tưởng Hồ Chí Minh.", src:"Văn kiện Đại hội XIII của Đảng, 2021" },
  note:["Đặc điểm giai đoạn 4","Nhận thức đi vào chiều sâu: từ khẳng định vị trí → xây dựng định nghĩa → đưa vào giảng dạy, tổ chức học tập và đấu tranh bảo vệ nền tảng tư tưởng."],
  notes:"Giai đoạn này có ba hướng vận động: hoàn thiện định nghĩa (2001, 2011); chuyển nhận thức thành hành động qua các chỉ thị học tập và làm theo, đặc biệt Chỉ thị 05 năm 2016 mở rộng thêm nội dung phong cách Hồ Chí Minh; và đấu tranh phản bác các quan điểm sai trái, xuyên tạc theo Nghị quyết 35 của Bộ Chính trị. Môn Tư tưởng Hồ Chí Minh trở thành môn học bắt buộc trong các trường đại học cũng là kết quả của quá trình này." });

/* ─────────────────── 12. NHẬN XÉT – ĐÁNH GIÁ ────────────── */
{
  const s = pres.addSlide(); chrome(s, "PHẦN IV · NHẬN XÉT & KẾT LUẬN");
  title(s, "NHẬN XÉT VỀ QUÁ TRÌNH NHẬN THỨC CỦA ĐẢNG");
  s.addImage({ path:IMG+"fig_nhanxet.png", x:7.15, y:1.52, w:5.60, h:3.38 });
  const it = [
    ["Là một quá trình lâu dài, liên tục", "Đi từ thấp đến cao, từ chưa đầy đủ đến ngày càng đầy đủ, toàn diện và sâu sắc — đúng quy luật của nhận thức."],
    ["Luôn gắn với thực tiễn cách mạng", "Mỗi bước phát triển về nhận thức đều gắn với một bước ngoặt của thực tiễn: 1930, 1945, 1951, 1986, 1991."],
    ["Không diễn ra một chiều, thẳng tắp", "Có lúc nhận thức chưa đúng, chưa đầy đủ; Đảng đã tự phê bình, nhận thức lại và khắc phục — thể hiện bản lĩnh khoa học."],
    ["Ngày nay tiếp tục được bổ sung, bảo vệ", "Vừa vận dụng, phát triển sáng tạo, vừa kiên quyết đấu tranh phản bác các quan điểm sai trái, xuyên tạc."]];
  let y = 1.50;
  it.forEach((b,i) => {
    chip(s, 0.62, y+0.02, String(i+1), i%2 ? "A8761A" : P.RED);
    s.addText(b[0], { x:1.22, y, w:5.55, h:0.30, isTextBox:true, margin:0, fontFace:BF,
      fontSize:13.5, bold:true, color:P.RED });
    s.addText(b[1], { x:1.22, y:y+0.32, w:5.55, h:0.76, isTextBox:true, margin:0, fontFace:BF,
      fontSize:11.6, color:P.INK, lineSpacing:15.5 });
    y += 1.16;
  });
  card(s, { x:7.15, y:5.08, w:5.60, h:1.64, fill:P.RED, line:P.RED });
  s.addText("LIÊN HỆ SINH VIÊN", { x:7.42, y:5.24, w:5.06, h:0.30, isTextBox:true, margin:0,
      fontFace:BF, fontSize:12.5, bold:true, color:P.GOLD });
  s.addText("Học đúng bản chất khoa học của tư tưởng Hồ Chí Minh, tránh học thuộc lòng hình thức; vận dụng vào học tập, rèn luyện đạo đức và tỉnh táo trước thông tin xuyên tạc trên mạng xã hội.",
    { x:7.42, y:5.56, w:5.06, h:1.02, isTextBox:true, margin:0, fontFace:BF, fontSize:11.5,
      color:"FBE9E4", lineSpacing:16 });
  s.addText("KẾT LUẬN: Nội hàm khái niệm càng sáng tỏ thì nhận thức của Đảng càng đầy đủ — đó là kết quả của gần một thế kỷ tổng kết thực tiễn và đổi mới tư duy lý luận.",
    { x:0.62, y:6.22, w:6.30, h:0.62, isTextBox:true, margin:0, fontFace:BF, fontSize:11.5,
      bold:true, italic:true, color:P.RED, lineSpacing:16 });
  s.addNotes("Đây là phần trả lời trực tiếp yêu cầu đưa ra nhận xét của đề bài. Bốn nhận xét nên trình bày gọn, nhấn mạnh nhận xét số 3: quá trình nhận thức không thẳng tắp, có quanh co, và chính việc Đảng dám nhận thức lại mới là biểu hiện của bản lĩnh khoa học. Kết thúc bằng liên hệ sinh viên rồi chuyển sang hai câu hỏi thảo luận.");
}

/* ───────────────── 13. CÂU HỎI THẢO LUẬN ────────────────── */
{
  const s = pres.addSlide();
  s.background = { path:IMG+"bg_title.png" };
  s.addText("PHẦN IV · THẢO LUẬN", { x:0.85, y:0.62, w:8, h:0.32, isTextBox:true, margin:0,
      fontFace:BF, fontSize:12, bold:true, color:P.GOLD, charSpacing:3 });
  s.addText("HAI CÂU HỎI THẢO LUẬN", { x:0.85, y:1.02, w:9.5, h:0.72, isTextBox:true, margin:0,
      fontFace:HF, fontSize:34, bold:true, color:P.WHITE });
  const qs = [
    ["CÂU HỎI 1", "Vì sao phải đến Đại hội VII (6/1991) Đảng ta mới chính thức khẳng định tư tưởng Hồ Chí Minh là nền tảng tư tưởng, kim chỉ nam cho hành động, trong khi tư tưởng ấy đã dẫn dắt cách mạng Việt Nam từ năm 1930? Điều đó nói lên đặc điểm gì của quá trình nhận thức lý luận?"],
    ["CÂU HỎI 2", "Trong bối cảnh chuyển đổi số và mạng xã hội phát triển mạnh hiện nay, sinh viên cần làm gì để việc học tập tư tưởng Hồ Chí Minh không dừng lại ở nhận thức mà trở thành hành động cụ thể, đồng thời góp phần đấu tranh phản bác các quan điểm sai trái, xuyên tạc?"]];
  let y = 2.12;
  qs.forEach((q,i) => {
    s.addShape(pres.ShapeType.roundRect, { x:0.85, y, w:8.55, h:1.86, rectRadius:0.10,
      fill:{ color:"6E080F" }, line:{ color:"A8571C", width:1.25 } });
    s.addShape(pres.ShapeType.ellipse, { x:1.12, y:y+0.30, w:0.62, h:0.62,
      fill:{ color:P.GOLD }, line:{ color:P.GOLD, width:1 } });
    s.addText(String(i+1), { x:1.12, y:y+0.30, w:0.62, h:0.62, isTextBox:true, margin:0,
      fontFace:BF, fontSize:24, bold:true, color:P.RED, align:"center", valign:"middle" });
    s.addText(q[0], { x:1.95, y:y+0.22, w:7.2, h:0.30, isTextBox:true, margin:0, fontFace:BF,
      fontSize:12, bold:true, color:P.GOLD, charSpacing:1.5 });
    s.addText(q[1], { x:1.95, y:y+0.54, w:7.25, h:1.14, isTextBox:true, margin:0, fontFace:BF,
      fontSize:13, color:"FBE9E4", lineSpacing:19 });
    y += 2.06;
  });
  s.addImage({ path:IMG+"fig_thaoluan.png", x:9.75, y:2.55, w:3.15, h:1.45 });
  s.addText("CẢM ƠN THẦY/CÔ VÀ CÁC BẠN\nĐÃ LẮNG NGHE!", { x:9.45, y:4.62, w:3.70, h:1.0,
      isTextBox:true, margin:0, fontFace:HF, fontSize:17, bold:true, color:P.GOLD,
      align:"center", lineSpacing:25 });
  s.addText("Nhóm 1 · Trưởng nhóm: Nguyễn Thành Đạt", { x:0.85, y:6.60, w:8.55, h:0.32,
      isTextBox:true, margin:0, fontFace:BF, fontSize:11.5, color:"E8C9C4" });
  s.addNotes("Hai câu hỏi thảo luận: câu 1 hướng vào phần lý luận, kiểm tra người nghe có nắm được tính quy luật của quá trình nhận thức không. Câu 2 hướng vào liên hệ thực tiễn với sinh viên. Nhóm xin lắng nghe ý kiến của thầy/cô và các bạn.");
}

pres.writeFile({ fileName:"Nhom1-Tu-tuong-Ho-Chi-Minh.pptx" })
  .then(f => console.log("OK ->", f));
