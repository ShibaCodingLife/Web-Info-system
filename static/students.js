$(document).ready(function () {
	$(".student-card").click(function (event) {
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
			number: student_card.find(".editor #student_id").val(),
			age: student_card.find(".editor #age").val(),
			sex: student_card.find(".editor #sex").val(),
			address: student_card.find(".editor #address").val(),
			sdept: student_card.find(".editor #department").val(),
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
					alert(response.info);
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
		new_student_card = $("#student-card-template").clone(
			(deepWithDataAndEvents = true)
		);
		new_student_card.removeAttr("id");
		new_student_card.css("display", "flex");
		new_student_card.insertBefore($("#student-card-template"));
	});

	$("#teacherName").click(function (event) {
		event.stopPropagation();
		$(".dropdown").toggleClass("show-dropdown");
	});

	$("#logout-btn").click(function (event) {
		event.stopPropagation();
		window.location.href = "/logout";
	});

	$("#search-btn").click(function (event) {
		event.stopPropagation();
		if (!$("#search-wrapper").hasClass("active")) {
			$("#search-wrapper").addClass("active");
			$("#search-input").focus();
			return;
		}
		let search_text = $("#search-input").val();
		window.location.href = "/search/" + search_text;
	});

	$(document).on("click", function () {
		$(".dropdown").removeClass("show-dropdown");
	});
});
