$(document).ready(function () {
    $(".student-card.student-card:not(.add)").click(function(event) {
        event.stopPropagation();
        if ($(this).hasClass("expanded")) {
            return;
        }
        $(this).toggleClass("expanded");
        $(this).find(".info, .editor").toggle();
      });

    $(".save-btn").click(function (event) {
        event.stopPropagation();
        let student_card = $(this).closest(".student-card");
        let studentData = {
            name: student_card.find(".editor #name").val(),
            number: student_card.find(".editor #student_id").text(),
            age: student_card.find(".editor #age").text(),
            sex: student_card.find(".editor #sex").text(),
            address: student_card.find(".editor #address").text(),
            sdept: student_card.find(".editor #department").text(),
        };
        let student_id = student_card.attr("data-student-id");
        let url;
        if (student_id === "-1") url = "/add_student";
        else url = "/update_student/" + student_id;

        $.ajax({
            url: url,
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify(studentData),
            success: function (response) {
                console.log(response);
                if (response.success) {
                    student_card.find(".info, .editor").toggle();
                    student_card.toggleClass("expanded");
                    student_card.find(".info #name").text(studentData.name);
                    student_card.find(".info #student_id").text(studentData.number);
                    student_card.find(".info #age").text(studentData.age);
                    student_card.find(".info #sex").text(studentData.sex);
                    student_card.find(".info #address").text(studentData.address);
                    student_card.find(".info #department").text(studentData.sdept);
                    student_card.attr("data-student-id", studentData.number);
                    if (student_id === "-1") {
                        student_card.removeClass("new-student-card");
                    }
                } else {
                    alert("学号重复,请确认后添加!");
                }
            },
            error: function (error) {
                console.log(error);
            },
        });
    });

    $(".delete-btn").click(function (event) {
        event.stopPropagation();
        let student_card = $(this).closest(".student-card");
        let delete_url = "/delete_student/" + student_card.attr("data-student-id");
        $.ajax({
            url: delete_url,
            type: "DELETE",
            success: function (response) {
                console.log(response);
                if (response.success) {
                    student_card.remove();
                } else {
                    alert(response.info);
                }
            },
            error: function (error) {
                console.log(error);
            },
        });
    });

    $(".cancel-btn").click(function (event) {
        event.stopPropagation();
        let student_card = $(this).closest(".student-card");
        if (student_card.attr("data-student-id") === "-1") {
            student_card.remove();
            return;
        }
        student_card.toggleClass("expanded");
        student_card.find(".info, .editor").toggle();
    });

    $(".add-btn").click(function (event) {
        event.stopPropagation();
        let student_card_template = $("#student-card-template");
        let new_student_card = student_card_template.clone(true);
        new_student_card.removeAttr("id");
        new_student_card.css("display", "flex");
        new_student_card.insertBefore(student_card_template);
        new_student_card.click();
    });

    $("#teacherName").click(function (event) {
        event.stopPropagation();
        $(".dropdown").toggleClass("show-dropdown");
        $(".dropdown-content").toggleClass("hidden");
        // $(this).siblings(".dropdown-content").toggleClass("show-dropdown");
    });

    $(".dropdown-content").click(function (event) {
        event.stopPropagation();
        window.location.href = "/logout";
    });

    $("#search-btn").click(function (event) {
        event.stopPropagation();
        let search_wrapper = $("#search-wrapper");
        let search_input = $("#search-input");
        if (!search_wrapper.hasClass("active")) {
            search_wrapper.addClass("active");
            $("#search-input").focus();
            return;
        }
        let search_text = search_input.val();
        if (search_text === "") {
            window.location.href = "/students";
            return;
        }
        window.location.href = "/search/" + search_text;
    });

    $("#delete-btn").click(function (event){
        // 获取所有被选中的学生卡片
        let selectedStudents = $(".form-check-input:checked");

        // 如果没有选中的学生，不执行任何操作
        if (selectedStudents.length === 0) {
            alert("请选择要删除的学生！");
            return;
        }

        // 收集选中学生的学号
        let studentIds = [];
        selectedStudents.each(function() {
            let studentId = $(this).closest(".student-card").data("student-id");
            studentIds.push(studentId);
        });

        // 发送请求到后端进行批量删除
        $.ajax({
            type: "POST",
            url: "/delete_students",
            contentType: "application/json;charset=UTF-8",
            data: JSON.stringify({ student_ids: studentIds }),
            success: function(response) {
                // 处理成功响应
                alert('学生删除成功!');
                selectedStudents.closest(".student-card").remove();
                // 刷新页面或执行其他操作
            },
            error: function(error) {
                // 处理错误响应
                alert("删除失败：" + error.responseJSON.message);
            }
        });

    });

    $(document).on("click", function () {
        $(".dropdown").removeClass("show-dropdown");
    });
});
