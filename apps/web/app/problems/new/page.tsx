import { Breadcrumb } from "../../../components/breadcrumb";
import { CreateObjectForm } from "../../../features/create/create-object-form";

export default function NewProblemPage() {
  return (
    <article>
      <Breadcrumb
        items={[
          { href: "/", label: "工作台" },
          { href: "/problems", label: "题目" },
          { label: "新建" },
        ]}
      />
      <CreateObjectForm operation="CreateProblem" heading="创建题目" extra="parts" />
    </article>
  );
}
